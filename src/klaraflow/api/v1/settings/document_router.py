from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os
import shutil
from pathlib import Path
import uuid

from klaraflow.crud import document_template_crud
from klaraflow.schemas import document_schema
from klaraflow.config.database import get_db
from klaraflow.dependencies.auth import get_current_active_admin
from klaraflow.models.user_model import User
from klaraflow.models.documents.document_submission_model import DocumentSubmission
from klaraflow.base.responses import create_response
from klaraflow.base.exceptions import APIException

router = APIRouter()

# Document Template Management Routes
@router.post(
    "/templates",
    response_model=document_schema.DocumentTemplateRead,
    status_code=status.HTTP_201_CREATED
)
async def create_document_template(
    template_data: document_schema.DocumentTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Create a new document template"""
    
    template = await document_template_crud.create_document_template(
        db=db,
        template_data=template_data,
        company_id=current_admin.company_id
    )
    
    return create_response(
        data=template,
        message="Document template created successfully",
        status_code=status.HTTP_201_CREATED
    )

@router.get(
    "/templates",
    response_model=List[document_schema.DocumentTemplateRead]
)
async def get_document_templates(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Get all document templates for the company"""
    
    templates = await document_template_crud.get_document_templates(
        db=db,
        company_id=current_admin.company_id,
        skip=skip,
        limit=limit
    )
    
    return create_response(
        data=templates,
        message="Document templates retrieved successfully",
        status_code=status.HTTP_200_OK
    )

@router.get(
    "/templates/{template_id}",
    response_model=document_schema.DocumentTemplateRead
)
async def get_document_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Get a specific document template"""
    
    template = await document_template_crud.get_document_template_by_id(
        db=db,
        template_id=template_id,
        company_id=current_admin.company_id
    )
    
    if not template:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Document template not found"
        )
    
    return create_response(
        data=template,
        message="Document template retrieved successfully",
        status_code=status.HTTP_200_OK
    )

@router.put(
    "/templates/{template_id}",
    response_model=document_schema.DocumentTemplateRead
)
async def update_document_template(
    template_id: int,
    template_data: document_schema.DocumentTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Update a document template"""
    
    template = await document_template_crud.update_document_template(
        db=db,
        template_id=template_id,
        template_data=template_data,
        company_id=current_admin.company_id
    )
    
    return create_response(
        data=template,
        message="Document template updated successfully",
        status_code=status.HTTP_200_OK
    )

@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_document_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Delete a document template"""
    
    await document_template_crud.delete_document_template(
        db=db,
        template_id=template_id,
        company_id=current_admin.company_id
    )
    
    return create_response(
        data=None,
        message="Document template deleted successfully",
        status_code=status.HTTP_204_NO_CONTENT
    )

# Document Upload Route (enhanced for local storage)
@router.post(
    "/upload/{template_id}",
    response_model=document_schema.DocumentUploadResponse
)
async def upload_document(
    template_id: int,
    employee_id: str = Form(...),
    fields: str = Form(...),  # JSON string of non-file fields
    files: List[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Upload document with form data (supporting local file storage)"""
    
    # Get the template to validate
    template = await document_template_crud.get_document_template_by_id(
        db=db,
        template_id=template_id,
        company_id=current_admin.company_id
    )
    
    if not template:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Document template not found"
        )
    
    # Create uploads directory if it doesn't exist
    uploads_dir = Path("uploads/documents")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Process file uploads
    file_paths = {}
    for file in files:
        if file.filename:
            # Generate unique filename
            file_extension = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = uploads_dir / unique_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Store relative path for database
            file_paths[file.filename] = str(file_path)
    
    # Parse fields JSON
    import json
    try:
        field_data = json.loads(fields)
    except json.JSONDecodeError:
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid fields JSON format"
        )
    
    # Save the document submission to database
    submission = DocumentSubmission(
        template_id=template_id,
        employee_id=employee_id,
        company_id=current_admin.company_id,
        field_values=field_data,
        file_paths=file_paths
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    
    upload_response = {
        "id": submission.id,
        "template_id": template_id,
        "employee_id": employee_id,
        "uploaded_at": submission.submitted_at.isoformat(),
        "file_paths": file_paths
    }
    
    return create_response(
        data=upload_response,
        message="Document uploaded successfully",
        status_code=status.HTTP_201_CREATED
    )