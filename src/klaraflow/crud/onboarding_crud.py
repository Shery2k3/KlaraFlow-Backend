from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from klaraflow.models.onboarding.session_model import OnboardingSession
from klaraflow.models.onboarding.task_model import OnboardingTask
from klaraflow.models.onboarding.document_model import OnboardingDocument
from klaraflow.models.onboarding.todo_item_model import TodoItem
from klaraflow.schemas import onboarding_schema
from klaraflow.core.security import create_access_token, get_hash_password
from klaraflow.core.email_service import send_onboarding_invitation
from klaraflow.crud import user_crud
from klaraflow.base.responses import create_response
from klaraflow.base.exceptions import APIException

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
        designation=invite_data.designation,
        department=invite_data.department,
        jobType=invite_data.jobType,
        hiringDate=invite_data.hiringDate,
        reportTo=invite_data.reportTo,
        grade=invite_data.grade,
        probationPeriod=invite_data.probationPeriod,
        dateOfBirth=invite_data.dateOfBirth,
        maritalStatus=invite_data.maritalStatus,
        nationality=invite_data.nationality,
        profile_picture_url=profile_picture_url
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
    session = await get_onboarding_session_for_user(db, user_email)
    
    from klaraflow.crud.onboarding_template_crud import get_onboarding_template_by_id
    template = await get_onboarding_template_by_id(db, template_id=session.template_id, company_id=session.company_id)
    
    # log template
    logger.info(f"Onboarding template for session {session.id}: {template}")
    
    todos = []
    required_documents = []
    optional_documents = []
    
    if template:
        # Pre-fetch existing tasks and documents for this session
        existing_tasks_result = await db.execute(select(OnboardingTask).where(OnboardingTask.session_id == session.id))
        existing_tasks = {task.todo_item_id: task for task in existing_tasks_result.scalars().all()}

        uploaded_docs_result = await db.execute(select(OnboardingDocument).where(OnboardingDocument.session_id == session.id))
        uploaded_doc_ids = {doc.document_template_id for doc in uploaded_docs_result.scalars().all()}
        
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
        await db.commit() # Commit new tasks
        
        todos = [
            onboarding_schema.TodoItemRead.model_validate(
                todo, 
                update={"is_completed": existing_tasks.get(todo.id).is_completed if todo.id in existing_tasks else False}
            ) 
            for todo in template.todos
        ]
        
        required_documents = [
            onboarding_schema.OnboardingDocumentRead.model_validate(doc, update={"uploaded": doc.id in uploaded_doc_ids})
            for doc in template.required_documents
        ]
        
        optional_documents = [
            onboarding_schema.OnboardingDocumentRead.model_validate(doc, update={"uploaded": doc.id in uploaded_doc_ids})
            for doc in template.optional_documents
        ]
    
    employee_data = {
        "id": session.id,
        "empId": session.empId,
        "firstName": session.firstName,
        "lastName": session.lastName,
        "email": session.new_employee_email,
        "phone": session.phone,
        "gender": session.gender,
        "userRole": session.userRole,
        "designation": session.designation,
        "department": session.department,
        "jobType": session.jobType,
        "hiringDate": session.hiringDate,
        "reportTo": session.reportTo,
        "grade": session.grade,
        "probationPeriod": session.probationPeriod,
        "dateOfBirth": session.dateOfBirth,
        "maritalStatus": session.maritalStatus,
        "nationality": session.nationality,
        "profilePic": session.profile_picture_url,
        "status": session.status,
    }
    
    todos = [
        onboarding_schema.TodoItemRead.model_validate(
            todo, 
            update={"is_completed": existing_tasks.get(todo.id).is_completed if todo.id in existing_tasks else False}
        ) 
        for todo in template.todos
    ]
    
    required_documents = [
        onboarding_schema.OnboardingDocumentRead.model_validate(doc, update={"uploaded": doc.id in uploaded_doc_ids})
        for doc in template.required_documents
    ]
    
    optional_documents = [
        onboarding_schema.OnboardingDocumentRead.model_validate(doc, update={"uploaded": doc.id in uploaded_doc_ids})
        for doc in template.optional_documents
    ]
    
    return onboarding_schema.OnboardingDataRead(
        id=session.id,
        employee_data=employee_data,
        todos=todos,
        required_documents=required_documents,
        optional_documents=optional_documents,
        current_step=session.current_step
    )

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

async def save_uploaded_document(db: AsyncSession, user_email: str, document_template_id: int, file_url: str):
    session = await get_onboarding_session_for_user(db, user_email)
    
    new_document = OnboardingDocument(
        session_id=session.id,
        document_template_id=document_template_id,
        file_url=file_url
    )
    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)
    return new_document

async def submit_onboarding(db: AsyncSession, user_email: str):
    session = await get_onboarding_session_for_user(db, user_email)
    session.status = "completed"
    
    # Update user status to active
    from klaraflow.crud import user_crud
    user = await user_crud.get_user_by_email(db, email=user_email)
    user.is_active = True
    
    await db.commit()