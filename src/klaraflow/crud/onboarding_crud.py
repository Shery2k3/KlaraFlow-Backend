from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status, UploadFile
from klaraflow.models.documents.document_submission_model import DocumentSubmission
from klaraflow.models.onboarding.session_model import OnboardingSession
from klaraflow.models.onboarding.task_model import OnboardingTask
from klaraflow.models.documents.document_submission_model import DocumentSubmission 
from klaraflow.schemas import onboarding_schema
from klaraflow.core.security import create_access_token, get_hash_password
from klaraflow.core.email_service import send_onboarding_invitation
from klaraflow.crud import document_template_crud, user_crud
from klaraflow.core.s3_service import s3_service
from klaraflow.base.exceptions import APIException
import json

import logging

logger = logging.getLogger("klaraflow.onboarding")
logging.basicConfig(
    level=logging.INFO,  # Or DEBUG for more details
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)

async def invite_new_employee(db: AsyncSession,invite_data: onboarding_schema.OnboardingInviteRequest,company_id: int, profile_picture_url: str = None):
    #? Check for existing pending invites
    existing_session = select(OnboardingSession).where(
        OnboardingSession.new_employee_email == invite_data.email,
        OnboardingSession.status == "pending"
    )
    result = await db.execute(existing_session)
    if result.scalar_one_or_none():
        raise APIException(status_code=status.HTTP_409_CONFLICT, message="An active invitation for this email already exists.", errors=["Duplicate invitation."])
    
    expires_delta = timedelta(hours=24)
    expires_at = datetime.now(timezone.utc) + expires_delta
    
    token_data = {
        "sub": invite_data.email, 
        "cid": company_id,
        "scope": "onboarding_invitation"
    }
    invitation_token = create_access_token(data=token_data, expires_delta=expires_delta)

    # We'll create the user with a placeholder, inactive status.
    # The actual user record will be fully created after onboarding.
    # For now, we store the essential info in the session.
    db_session = OnboardingSession(
        company_id=company_id,
        new_employee_email=invite_data.email,
        invitation_token=invitation_token,
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc),
        empId=invite_data.empId,
        firstName=invite_data.firstName,
        lastName=invite_data.lastName,
        phone=invite_data.phone,
        gender=invite_data.gender,
        userRole=invite_data.userRole,
        designation_id=int(invite_data.designation),
        department_id=int(invite_data.department),
        jobType=invite_data.jobType,
        hiringDate=invite_data.hiringDate,
        reportTo=invite_data.reportTo,
        grade=invite_data.grade,
        probationPeriod=invite_data.probationPeriod,
        dateOfBirth=invite_data.dateOfBirth,
        maritalStatus=invite_data.maritalStatus,
        nationality=invite_data.nationality,
        profile_picture_url=profile_picture_url,
        template_id=invite_data.onboardingTemplateId
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    
    await send_onboarding_invitation(
        email_to=invite_data.email, 
        token=invitation_token
    )
    
    return db_session

async def get_session_by_token(db: AsyncSession, token: str) -> OnboardingSession:
    statement = select(OnboardingSession).where(OnboardingSession.invitation_token == token)
    result = await db.execute(statement)
    session = result.scalar_one_or_none()
    
    if not session:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND, message="Invitation link is invalid or has been used.", errors=["Invalid or used token."])
    
    if session.status != "pending":
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST, message="This invitation has already been used or is no longer valid.", errors=["Invitation not pending."])

    if session.expires_at < datetime.now(timezone.utc):
        session.status = "expired"
        await db.commit()
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST, message="This invitation link has expired.", errors=["Token expired."])
        
    return session

async def activate_employee_account(db: AsyncSession, *, activation_data: onboarding_schema.OnboardingActivationRequest):
    # 1. Get and validate the session using our new function
    session = await get_session_by_token(db, token=activation_data.token)
    
    # 2. Hash the new password provided by the employee
    hashed_password = get_hash_password(activation_data.password)
    
    # 3. Create the permanent user record in the 'users' table
    new_user = await user_crud.create_user_from_onboarding(
        db,
        session=session,
        hashed_password=hashed_password
    )
    
    # 4. Mark the temporary onboarding session as 'in_progress'
    session.status = "in_progress"
    await db.commit()
    
    # 5. Create a login token for the new user so they are immediately logged in
    login_token = create_access_token(data={"sub": new_user.email})
    
    return {"access_token": login_token, "token_type": "bearer"}

async def update_onboarding_step(db: AsyncSession, token: str, step_data: onboarding_schema.OnboardingStepUpdateRequest) -> OnboardingSession:
    session = await get_session_by_token(db, token=token)
    session.current_step = step_data.current_step
    await db.commit()
    await db.refresh(session)
    return session

async def get_onboarding_session_for_user(db: AsyncSession, user_email: str) -> OnboardingSession:
    statement = select(OnboardingSession).where(
        OnboardingSession.new_employee_email == user_email,
        OnboardingSession.status == "in_progress"
    )
    result = await db.execute(statement)
    session = result.scalar_one_or_none()
    if not session:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND, message="No active onboarding session found", errors=["No onboarding session"])
    return session

async def get_onboarding_data_for_user(db: AsyncSession, user_email: str) -> onboarding_schema.OnboardingDataRead:
    try:
        session = await get_onboarding_session_for_user(db, user_email)
        logger.info(f"Retrieved onboarding session for user {user_email}: {session.id}")
        
        from klaraflow.crud.onboarding_template_crud import get_onboarding_template_by_id
        template = await get_onboarding_template_by_id(db, template_id=session.template_id, company_id=session.company_id)
        logger.info(f"Onboarding template for session {session.id}: {template}")
        
        todos = []
        required_documents = []
        optional_documents = []
        
        if template:
            logger.info(f"Template found, processing todos and documents for session {session.id}")
            # Pre-fetch existing tasks and documents for this session
            existing_tasks_result = await db.execute(select(OnboardingTask).where(OnboardingTask.session_id == session.id))
            existing_tasks = {task.todo_item_id: task for task in existing_tasks_result.scalars().all()}
            logger.debug(f"Existing tasks for session {session.id}: {list(existing_tasks.keys())}")

            uploaded_docs_result = await db.execute(
                select(DocumentSubmission).where(DocumentSubmission.employee_id == session.empId)
            )
            uploaded_doc_ids = {doc.template_id for doc in uploaded_docs_result.scalars().all()}
            logger.debug(f"Uploaded doc IDs for session {session.id} from submissions: {uploaded_doc_ids}")
            
            # Create tasks for todos that don't have one yet
            for todo_template in template.todos:
                if todo_template.id not in existing_tasks:
                    new_task = OnboardingTask(
                        session_id=session.id,
                        todo_item_id=todo_template.id,
                        title=todo_template.title,
                        description=todo_template.description,
                        is_completed=False
                    )
                    db.add(new_task)
                    existing_tasks[todo_template.id] = new_task
                    logger.info(f"Created new task for todo {todo_template.id} in session {session.id}")
            await db.commit()  # Commit new tasks
            logger.info(f"Committed new tasks for session {session.id}")
            
            # Build todo representations and attach completion status returned as plain dicts
            todos = []
            for todo in template.todos:
                todo_model = onboarding_schema.TodoItemRead.model_validate(todo)
                todo_dict = todo_model.model_dump()
                todo_dict["is_completed"] = existing_tasks.get(todo.id).is_completed if todo.id in existing_tasks else False
                todos.append(todo_dict)
            logger.debug(f"Processed {len(todos)} todos for session {session.id}")
            
            # Build document representations and set 'uploaded' flag on plain dicts
            # Convert DocumentTemplate and nested DocumentField ORM objects into serializable dicts
            required_documents = []
            for doc in template.required_documents:
                # Convert fields into simple dicts
                fields_list = []
                for f in getattr(doc, "fields", []) or []:
                    fields_list.append({
                        "id": getattr(f, "id", None),
                        "label": getattr(f, "label", None),
                        "field_type": getattr(f.field_type, "value", f.field_type) if f is not None else None,
                        "placeholder": getattr(f, "placeholder", None),
                        "description": getattr(f, "description", None),
                        "required": getattr(f, "required", False),
                        "width": getattr(f.width, "value", f.width) if f is not None else None,
                        "order_index": getattr(f, "order_index", None),
                        "created_at": getattr(f, "created_at", None),
                    })

                doc_dict = {
                    "id": getattr(doc, "id", None),
                    "name": getattr(doc, "name", None),
                    "fields": fields_list,
                    "required": True,
                    "uploaded": doc.id in uploaded_doc_ids,
                    "created_at": getattr(doc, "created_at", None),
                    "updated_at": getattr(doc, "updated_at", None),
                }
                required_documents.append(doc_dict)
            logger.debug(f"Processed {len(required_documents)} required documents for session {session.id}")

            optional_documents = []
            for doc in template.optional_documents:
                fields_list = []
                for f in getattr(doc, "fields", []) or []:
                    fields_list.append({
                        "id": getattr(f, "id", None),
                        "label": getattr(f, "label", None),
                        "field_type": getattr(f.field_type, "value", f.field_type) if f is not None else None,
                        "placeholder": getattr(f, "placeholder", None),
                        "description": getattr(f, "description", None),
                        "required": getattr(f, "required", False),
                        "width": getattr(f.width, "value", f.width) if f is not None else None,
                        "order_index": getattr(f, "order_index", None),
                        "created_at": getattr(f, "created_at", None),
                    })

                doc_dict = {
                    "id": getattr(doc, "id", None),
                    "name": getattr(doc, "name", None),
                    "fields": fields_list,
                    "required": False,
                    "uploaded": doc.id in uploaded_doc_ids,
                    "created_at": getattr(doc, "created_at", None),
                    "updated_at": getattr(doc, "updated_at", None),
                }
                optional_documents.append(doc_dict)
            logger.debug(f"Processed {len(optional_documents)} optional documents for session {session.id}")
        else:
            logger.warning(f"No template found for session {session.id} (template_id={session.template_id}, company_id={session.company_id})")
        
        logger.debug(f"Employee data prepared for session {session.id}")

        logger.info(f"Returning onboarding data for session {session.id}")
        # Return a simplified view matching OnboardingDataRead
        return onboarding_schema.OnboardingDataRead(
            new_employee_email=session.new_employee_email,
            firstName=session.firstName,
            lastName=session.lastName,
            empId=session.empId,
            phone=session.phone,
            gender=session.gender,
            dateOfBirth=session.dateOfBirth,
            maritalStatus=session.maritalStatus,
            nationality=session.nationality,
            profilePic=session.profile_picture_url,
            status=session.status,
            current_step=session.current_step,
            todos=todos,
            required_documents=required_documents,
            optional_documents=optional_documents,
        )
    except Exception as e:
        logger.error(f"Error in get_onboarding_data_for_user for user {user_email}: {str(e)}", exc_info=True)
        raise

async def update_todo_for_user(db: AsyncSession, user_email: str, todo_id: int, completed: bool):
    session = await get_onboarding_session_for_user(db, user_email)
    
    statement = select(OnboardingTask).where(
        OnboardingTask.session_id == session.id,
        OnboardingTask.todo_item_id == todo_id
    )
    result = await db.execute(statement)
    task_to_update = result.scalar_one_or_none()

    if not task_to_update:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND, message="Todo item not found for this session")

    task_to_update.is_completed = completed
    await db.commit()
    return {"message": "Todo updated successfully"}

async def submit_onboarding(db: AsyncSession, user_email: str):
    session = await get_onboarding_session_for_user(db, user_email)
    session.status = "submitted"
    
    await db.commit()

async def update_onboarding_review_for_user(
    db: AsyncSession,
    user_email: str,
    update_data: dict,
    profile_file: UploadFile | None = None
):
    """Update the onboarding session fields that the user is allowed to change
    and optionally upload a new profile picture to S3.
    """
    session = await get_onboarding_session_for_user(db, user_email)

    # Allowed fields to be updated by the user
    allowed = {
        "firstName",
        "lastName",
        "email",
        "phone",
        "gender",
        "dateOfBirth",
        "maritalStatus",
        "nationality",
    }

    for key, value in update_data.items():
        if key in allowed and value is not None:
            # Map email -> new_employee_email on the session
            if key == "email":
                session.new_employee_email = value
            else:
                setattr(session, key, value)

    # Handle profile picture upload if provided
    if profile_file is not None:
        try:
            file_url = await s3_service.upload_file(profile_file, folder=f"onboarding/{session.id}/profile")
            session.profile_picture_url = file_url
        except Exception as e:
            logger.error(f"Failed to upload profile picture for session {session.id}: {e}")
            raise APIException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Failed to upload profile picture", errors=[str(e)])

    # If email was updated, also update the session email field
    await db.commit()
    await db.refresh(session)

    # Return updated onboarding data view
    return await get_onboarding_data_for_user(db, user_email=session.new_employee_email)

async def increment_step_for_user(db: AsyncSession, user_email: str):
    session = await get_onboarding_session_for_user(db, user_email)
    session.current_step += 1
    await db.commit()
    
async def submit_onboarding_document(
    db: AsyncSession,
    *,
    document_template_id: int,
    employee_id: str,
    company_id: int,
    fields_data: str,
    files: List[UploadFile]
) -> DocumentSubmission:
    """
    Handles the submission of a complete onboarding document, including
    all field types and file uploads.
    """
    # 1. Validate the template
    template = await document_template_crud.get_document_template_by_id(
        db, template_id=document_template_id, company_id=company_id
    )
    if not template:
        raise APIException(status_code=404, message="Document template not found")

    # 2. Upload files to S3
    file_paths = {}
    for file in files:
        if file.filename:
            folder = f"onboarding_documents/{company_id}/{employee_id}"
            file_url = await s3_service.upload_file(file, folder=folder)
            # Use the field name from the frontend as the key
            file_paths[file.filename] = file_url

    # 3. Parse the JSON fields data
    try:
        field_values = json.loads(fields_data)
    except json.JSONDecodeError:
        raise APIException(status_code=400, message="Invalid JSON format for fields")

    # 4. Create the DocumentSubmission record
    submission = DocumentSubmission(
        template_id=document_template_id,
        employee_id=employee_id,
        company_id=company_id,
        field_values=field_values,
        file_paths=file_paths,
        status="submitted"
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


async def list_onboarding_sessions(
    db: AsyncSession,
    company_id: int | None = None,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[onboarding_schema.OnboardingSessionRead]:
    """Return onboarding sessions optionally filtered by company and status.

    - company_id: if provided, restrict results to that company
    - status: if provided, filter by onboarding session status (pending, in_progress, submitted, expired, etc.)
    - limit/offset: simple pagination
    Returns a list of Pydantic-validated OnboardingSessionRead objects.
    """
    stmt = select(OnboardingSession)
    if company_id is not None:
        stmt = stmt.where(OnboardingSession.company_id == company_id)
    if status is not None:
        stmt = stmt.where(OnboardingSession.status == status)
    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    sessions = result.scalars().all()

    # Convert ORM objects to Pydantic models for a stable shape
    sessions_out: list[onboarding_schema.OnboardingSessionRead] = []
    for s in sessions:
        try:
            sessions_out.append(onboarding_schema.OnboardingSessionRead.model_validate(s))
        except Exception:
            # Fallback: build minimal dict if validation fails for any reason
            sessions_out.append(onboarding_schema.OnboardingSessionRead(
                id=getattr(s, "id", None),
                company_id=getattr(s, "company_id", None),
                new_employee_email=getattr(s, "new_employee_email", None),
                status=getattr(s, "status", None),
                created_at=getattr(s, "created_at", None),
                expires_at=getattr(s, "expires_at", None),
                current_step=getattr(s, "current_step", 0),
            ))

    return sessions_out
    await db.commit()
    await db.refresh(submission)
    return submission