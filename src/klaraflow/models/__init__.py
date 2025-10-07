# In BE/src/klaraflow/models/__init__.py

# This file imports all models, making them available to SQLAlchemy's mapper
# before any relationships are configured.

from .base import Base
from .company_model import Company
from .user_model import User
from .onboarding.session_model import OnboardingSession
from .onboarding.task_model import OnboardingTask
from .onboarding.todo_item_model import TodoItem
from .onboarding.onboarding_template_model import OnboardingTemplate
from .settings.document_template_model import DocumentTemplate, DocumentField
from .documents.document_submission_model import DocumentSubmission
from .department_model import Department
from .designation_model import Designation

# Note: Timesheet models are imported separately in alembic/env.py
# to avoid circular imports. They are at klaraflow.timesheet.models