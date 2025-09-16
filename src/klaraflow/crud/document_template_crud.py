from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import status
from typing import List, Optional

from klaraflow.models.settings.document_template_model import DocumentTemplate, DocumentField
from klaraflow.schemas.document_schema import (
    DocumentTemplateCreate, 
    DocumentTemplateUpdate,
    DocumentFieldCreate
)
from klaraflow.base.exceptions import APIException

async def create_document_template(
    db: AsyncSession, 
    *, 
    template_data: DocumentTemplateCreate, 
    company_id: int
) -> DocumentTemplate:
    """Create a new document template with fields"""
    
    # Create the template
    db_template = DocumentTemplate(
        name=template_data.name,
        company_id=company_id
    )
    db.add(db_template)
    await db.flush()  # Get the ID without committing
    
    # Create fields
    for idx, field_data in enumerate(template_data.fields):
        db_field = DocumentField(
            template_id=db_template.id,
            label=field_data.label,
            field_type=field_data.field_type,
            placeholder=field_data.placeholder,
            description=field_data.description,
            required=field_data.required,
            width=field_data.width,
            order_index=field_data.order_index or idx
        )
        db.add(db_field)
    
    await db.commit()
    await db.refresh(db_template)
    
    # Load the template with fields
    result = await db.execute(
        select(DocumentTemplate)
        .options(selectinload(DocumentTemplate.fields))
        .where(DocumentTemplate.id == db_template.id)
    )
    return result.scalar_one()

async def get_document_templates(
    db: AsyncSession, 
    company_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[DocumentTemplate]:
    """Get all document templates for a company"""
    
    result = await db.execute(
        select(DocumentTemplate)
        .options(selectinload(DocumentTemplate.fields))
        .where(DocumentTemplate.company_id == company_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_document_template_by_id(
    db: AsyncSession, 
    template_id: int, 
    company_id: int
) -> Optional[DocumentTemplate]:
    """Get a specific document template by ID"""
    
    result = await db.execute(
        select(DocumentTemplate)
        .options(selectinload(DocumentTemplate.fields))
        .where(
            DocumentTemplate.id == template_id,
            DocumentTemplate.company_id == company_id
        )
    )
    return result.scalar_one_or_none()

async def update_document_template(
    db: AsyncSession,
    *,
    template_id: int,
    template_data: DocumentTemplateUpdate,
    company_id: int
) -> DocumentTemplate:
    """Update a document template"""
    
    # Get existing template
    db_template = await get_document_template_by_id(db, template_id, company_id)
    if not db_template:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Document template not found"
        )
    
    # Update basic fields
    if template_data.name is not None:
        db_template.name = template_data.name
    
    # Update fields if provided
    if template_data.fields is not None:
        # Delete existing fields
        for field in db_template.fields:
            await db.delete(field)
        
        # Create new fields
        for idx, field_data in enumerate(template_data.fields):
            db_field = DocumentField(
                template_id=db_template.id,
                label=field_data.label,
                field_type=field_data.field_type,
                placeholder=field_data.placeholder,
                description=field_data.description,
                required=field_data.required,
                width=field_data.width,
                order_index=field_data.order_index or idx
            )
            db.add(db_field)
    
    await db.commit()
    await db.refresh(db_template)
    
    # Reload with fields
    result = await db.execute(
        select(DocumentTemplate)
        .options(selectinload(DocumentTemplate.fields))
        .where(DocumentTemplate.id == template_id)
    )
    return result.scalar_one()

async def delete_document_template(
    db: AsyncSession,
    template_id: int,
    company_id: int
) -> bool:
    """Delete a document template"""
    
    db_template = await get_document_template_by_id(db, template_id, company_id)
    if not db_template:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Document template not found"
        )
    
    await db.delete(db_template)
    await db.commit()
    return True