from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import insert, delete
from fastapi import status
from typing import List, Optional

from klaraflow.models.onboarding.onboarding_template_model import (
    OnboardingTemplate,
    onboarding_template_required_documents,
    onboarding_template_optional_documents
)
from klaraflow.models.onboarding.todo_item_model import TodoItem
from klaraflow.models.onboarding.task_model import OnboardingTask
from klaraflow.models.settings.document_template_model import DocumentTemplate
from klaraflow.schemas.onboarding_schema import (
    OnboardingTemplateCreate,
    OnboardingTemplateUpdate,
    TodoItemCreate
)
from sqlalchemy.orm import selectinload
from klaraflow.models.onboarding.onboarding_template_model import OnboardingTemplate
from klaraflow.base.exceptions import APIException

async def create_onboarding_template(
    db: AsyncSession,
    *,
    template_data: OnboardingTemplateCreate,
    company_id: int
) -> OnboardingTemplate:
    """Create a new onboarding template with todos and document associations"""
    
    # Create the template
    db_template = OnboardingTemplate(
        name=template_data.name,
        company_id=company_id
    )
    db.add(db_template)
    await db.flush()  # Get the ID without committing
    
    # Create todos
    for idx, todo_data in enumerate(template_data.todos):
        db_todo = TodoItem(
            template_id=db_template.id,
            title=todo_data.title,
            description=todo_data.description,
            order_index=todo_data.order_index or idx
        )
        db.add(db_todo)
    
    # Associate required documents
    if template_data.required_document_ids:
        # Verify document templates belong to the same company
        required_docs = await db.execute(
            select(DocumentTemplate.id).where(
                DocumentTemplate.id.in_(template_data.required_document_ids),
                DocumentTemplate.company_id == company_id
            )
        )
        valid_required_ids = required_docs.scalars().all()
        
        # Insert associations
        for doc_id in valid_required_ids:
            await db.execute(
                insert(onboarding_template_required_documents).values(
                    onboarding_template_id=db_template.id,
                    document_template_id=doc_id
                )
            )
    
    # Associate optional documents
    if template_data.optional_document_ids:
        # Verify document templates belong to the same company
        optional_docs = await db.execute(
            select(DocumentTemplate.id).where(
                DocumentTemplate.id.in_(template_data.optional_document_ids),
                DocumentTemplate.company_id == company_id
            )
        )
        valid_optional_ids = optional_docs.scalars().all()
        
        # Insert associations
        for doc_id in valid_optional_ids:
            await db.execute(
                insert(onboarding_template_optional_documents).values(
                    onboarding_template_id=db_template.id,
                    document_template_id=doc_id
                )
            )
    
    await db.commit()
    await db.refresh(db_template)
    
    # Load the template with all relationships
    result = await db.execute(
        select(OnboardingTemplate)
        .options(
            selectinload(OnboardingTemplate.todos),
            selectinload(OnboardingTemplate.required_documents).selectinload(DocumentTemplate.fields),
            selectinload(OnboardingTemplate.optional_documents).selectinload(DocumentTemplate.fields)
        )
        .where(OnboardingTemplate.id == db_template.id)
    )
    return result.scalar_one()

async def get_onboarding_templates(
    db: AsyncSession,
    company_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[OnboardingTemplate]:
    """Get all onboarding templates for a company"""
    
    result = await db.execute(
        select(OnboardingTemplate)
        .options(
            selectinload(OnboardingTemplate.todos),
            selectinload(OnboardingTemplate.required_documents).selectinload(DocumentTemplate.fields),
            selectinload(OnboardingTemplate.optional_documents).selectinload(DocumentTemplate.fields)
        )
        .where(OnboardingTemplate.company_id == company_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_onboarding_template_by_id(
    db: AsyncSession,
    template_id: int,
    company_id: int
) -> Optional[OnboardingTemplate]:
    """Get a specific onboarding template by ID"""
    
    result = await db.execute(
        select(OnboardingTemplate)
        .options(
            selectinload(OnboardingTemplate.todos), 
            # Eagerly load related DocumentTemplate.fields so reading attributes
            # during Pydantic model validation doesn't trigger async lazy loads
            selectinload(OnboardingTemplate.required_documents).selectinload(DocumentTemplate.fields),
            selectinload(OnboardingTemplate.optional_documents).selectinload(DocumentTemplate.fields)
        )
        .where(
            OnboardingTemplate.id == template_id,
            OnboardingTemplate.company_id == company_id
        )
    )
    return result.scalar_one_or_none()

async def update_onboarding_template(
    db: AsyncSession,
    *,
    template_id: int,
    template_data: OnboardingTemplateUpdate,
    company_id: int
) -> OnboardingTemplate:
    """Update an onboarding template"""
    
    # Get existing template
    db_template = await get_onboarding_template_by_id(db, template_id, company_id)
    if not db_template:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Onboarding template not found"
        )
    
    # Update basic fields
    if template_data.name is not None:
        db_template.name = template_data.name
    
    # Update todos if provided
    if template_data.todos is not None:
        # Upsert todos: update existing ones, create new ones, and only delete
        # template todos that are not present in the incoming list AND not
        # referenced by any onboarding session tasks.
        existing_todos = {t.id: t for t in db_template.todos if t.id is not None}
        incoming_ids = set()

        for idx, todo_data in enumerate(template_data.todos):
            incoming_id = getattr(todo_data, "id", None)
            if incoming_id:
                incoming_ids.add(incoming_id)
                if incoming_id in existing_todos:
                    # update existing
                    todo = existing_todos[incoming_id]
                    todo.title = todo_data.title
                    todo.description = todo_data.description
                    todo.order_index = todo_data.order_index or idx
                else:
                    # client supplied an id that doesn't belong to this template -> treat as new
                    db_todo = TodoItem(
                        template_id=db_template.id,
                        title=todo_data.title,
                        description=todo_data.description,
                        order_index=todo_data.order_index or idx
                    )
                    db.add(db_todo)
            else:
                # new todo
                db_todo = TodoItem(
                    template_id=db_template.id,
                    title=todo_data.title,
                    description=todo_data.description,
                    order_index=todo_data.order_index or idx
                )
                db.add(db_todo)

        # Determine which existing todos were removed by the client
        to_remove_ids = [eid for eid in existing_todos.keys() if eid not in incoming_ids]
        for eid in to_remove_ids:
            # Prevent deletion if any onboarding session task references this todo
            ref = await db.execute(
                select(OnboardingTask.id).where(OnboardingTask.todo_item_id == eid).limit(1)
            )
            if ref.scalar_one_or_none():
                # Abort with a clear API error so frontend can decide (or user can soft-delete)
                raise APIException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Cannot remove todo that is referenced by onboarding sessions",
                )
            # safe to delete
            await db.delete(existing_todos[eid])
    
    # Update document associations if provided
    if template_data.required_document_ids is not None:
        # Clear existing required document associations
        await db.execute(
            delete(onboarding_template_required_documents).where(
                onboarding_template_required_documents.c.onboarding_template_id == db_template.id
            )
        )
        
        # Add new required document associations
        if template_data.required_document_ids:
            # Verify document templates belong to the same company
            required_docs = await db.execute(
                select(DocumentTemplate.id).where(
                    DocumentTemplate.id.in_(template_data.required_document_ids),
                    DocumentTemplate.company_id == company_id
                )
            )
            valid_required_ids = required_docs.scalars().all()
            
            # Insert new associations
            for doc_id in valid_required_ids:
                await db.execute(
                    insert(onboarding_template_required_documents).values(
                        onboarding_template_id=db_template.id,
                        document_template_id=doc_id
                    )
                )
    
    if template_data.optional_document_ids is not None:
        # Clear existing optional document associations
        await db.execute(
            delete(onboarding_template_optional_documents).where(
                onboarding_template_optional_documents.c.onboarding_template_id == db_template.id
            )
        )
        
        # Add new optional document associations
        if template_data.optional_document_ids:
            # Verify document templates belong to the same company
            optional_docs = await db.execute(
                select(DocumentTemplate.id).where(
                    DocumentTemplate.id.in_(template_data.optional_document_ids),
                    DocumentTemplate.company_id == company_id
                )
            )
            valid_optional_ids = optional_docs.scalars().all()
            
            # Insert new associations
            for doc_id in valid_optional_ids:
                await db.execute(
                    insert(onboarding_template_optional_documents).values(
                        onboarding_template_id=db_template.id,
                        document_template_id=doc_id
                    )
                )
    
    await db.commit()
    await db.refresh(db_template)
    
    # Reload with all relationships
    result = await db.execute(
        select(OnboardingTemplate)
        .options(
            selectinload(OnboardingTemplate.todos),
            selectinload(OnboardingTemplate.required_documents).selectinload(DocumentTemplate.fields),
            selectinload(OnboardingTemplate.optional_documents).selectinload(DocumentTemplate.fields)
        )
        .where(OnboardingTemplate.id == template_id)
    )
    return result.scalar_one()

async def delete_onboarding_template(
    db: AsyncSession,
    template_id: int,
    company_id: int
) -> bool:
    """Delete an onboarding template"""
    
    db_template = await get_onboarding_template_by_id(db, template_id, company_id)
    if not db_template:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Onboarding template not found"
        )
    
    await db.delete(db_template)
    await db.commit()
    return True