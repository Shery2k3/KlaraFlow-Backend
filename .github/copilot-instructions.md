# KlaraFlow HRM Backend - Copilot Instructions

## Repository Overview
**Project**: KlaraFlow HRM - Multi-tenant HR Management SaaS Platform  
**Tech Stack**: Python 3.12+, FastAPI 0.115+, SQLAlchemy 2.0+ (async), PostgreSQL, Alembic  
**Package Manager**: Poetry 2.x  
**Size**: Small (~50 Python files, ~800KB)

## Critical Setup - DO THIS FIRST

### 1. Environment Configuration
**⚠️ CRITICAL**: Create `.env.development` file before ANY commands. Missing this causes `ValidationError`.

Required 14 environment variables (see `src/klaraflow/config/settings.py`):
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
DATABASE_URL_ASYNC=postgresql+asyncpg://user:pass@localhost:5432/dbname
SECRET_KEY=your_secret_key_here
JWT_ALG=HS256
ENVIRONMENT=development
DEBUG=true
MAIL_USERNAME=email@example.com
MAIL_PASSWORD=password
MAIL_FROM=noreply@klaraflow.io
MAIL_PORT=587
MAIL_SERVER=smtp.example.com
MAIL_STARTTLS=true
MAIL_SSL_TLS=false
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET_NAME=bucket-name
AWS_REGION=us-east-1
```

### 2. Installation
**ALWAYS** run in order:
```bash
pip install poetry                    # If not installed
poetry install                        # Install deps (~1-2 min)
poetry run python -c "from klaraflow.config.settings import settings; print('✅ Setup complete')"  # Verify
```

## Essential Commands

### Run Development Server
```bash
poetry run poe dev                    # Recommended (port 3001, auto-reload)
poetry run uvicorn klaraflow.main:app --reload --port 3001  # Alternative
```
**Access**: `http://localhost:3001/docs` (Swagger UI), `/health` (health check)  
**Note**: Requires PostgreSQL running

### Database Migrations (Alembic)
**⚠️ Requires**: `.env.development` with valid DATABASE_URL

```bash
poetry run alembic history            # View migrations (no DB needed)
poetry run alembic current            # Check current version (needs DB)
poetry run alembic upgrade head       # Apply migrations (needs DB)
poetry run alembic revision --autogenerate -m "description"  # Create migration
```
**Migrations**: `alembic/versions/` - Current: `c70eb0b20193` → `86c6eaea8622`

### Database Seeding
```bash
poetry run python -m scripts.seeder   # Creates company "KlaraFlow" and admin user
```
**Admin credentials**: `admin@klaraflow.io` / `klaraflow` (change in production)

### Testing & Linting
- **No test suite configured** - No pytest, no linters (flake8/ruff/black)
- Manual test: `poetry run python tests/test_db_connection.py`
- **When adding tests**: Use pytest + httpx following FastAPI patterns

## Project Structure

## Project Structure

```
src/klaraflow/
├── main.py                  # FastAPI app entry point
├── api/v1/                  # Route handlers by feature
│   ├── auth_router.py       # Authentication (/api/v1/auth)
│   ├── onboarding_router.py # Onboarding (/api/v1/onboarding)
│   ├── employees/           # Employee management
│   ├── company_settings/    # Departments, designations
│   └── settings/            # Templates (documents, onboarding)
├── base/                    # Base classes & utilities
│   ├── exceptions.py        # Custom APIException class
│   └── responses.py         # Standard response models
├── config/
│   ├── database.py          # DB connection (db_manager, get_db)
│   └── settings.py          # Pydantic settings (loads .env.development)
├── core/                    # Core services
│   ├── email_service.py     # Email sending (fastapi-mail)
│   ├── s3_service.py        # AWS S3 uploads
│   └── security.py          # Password hashing, JWT tokens
├── crud/                    # Database operations
├── dependencies/            # FastAPI dependencies
├── models/                  # SQLAlchemy ORM models
│   ├── base.py             # Base model
│   ├── company_model.py    # Tenant root (multi-tenant)
│   ├── user_model.py       # User accounts
│   ├── onboarding/         # Sessions, tasks, templates, todos
│   ├── documents/          # Document submissions
│   └── settings/           # Document templates
├── schemas/                # Pydantic validation schemas
└── services/               # Business logic

alembic/                    # Database migrations
├── env.py                  # Migration environment
├── versions/               # Migration files
└── script.py.mako          # Template

Key files:
- pyproject.toml            # Poetry deps, poe tasks
- alembic.ini               # Alembic config
- api_endpoints.md          # API documentation
- todos/todos.MD            # Known technical debt
```

## Architecture Patterns

**Multi-tenant**: All data scoped by `company_id`, Company is tenant root  
**Async throughout**: Use `async`/`await` everywhere - AsyncSession, async routes  
**Session management**: Use `Depends(get_db)` in routes, auto-commit/rollback  
**Error handling**: Raise `APIException` for business errors (see `base/exceptions.py`)  
**API routes**: All under `/api/v1/`, grouped by feature with tags

## Key Models & Relationships

**Core Models** (see `src/klaraflow/models/__init__.py`):
- `Company` - Tenant root (multi-tenant)
- `User` - Authentication & accounts
- `Department` / `Designation` - Org structure
- `OnboardingSession` - Employee onboarding process
- `OnboardingTemplate` - Reusable onboarding blueprints
- `TodoItem` - Onboarding checklist blueprint items
- `OnboardingTask` - Todo instance for specific session
- `DocumentTemplate` - Required/optional document definitions
- `DocumentSubmission` - Uploaded documents

**Relationships**: User→Company (M:1), OnboardingSession→OnboardingTemplate (M:1), OnboardingTask→OnboardingSession (M:1), OnboardingTask→TodoItem (M:1)

## API Endpoints

See `api_endpoints.md` for full details. Key routes:
- `/api/v1/auth` - signup, login, activate
- `/api/v1/onboarding` - invite, session, todos, documents, submit
- `/api/v1/document` - Document template CRUD
- `/api/v1/onboarding-template` - Onboarding template CRUD
- `/api/v1/settings/departments` - Department CRUD
- `/api/v1/settings/designations` - Designation CRUD
- `/api/v1/employees` - Employee management

## Common Errors & Solutions

**Error**: `ValidationError: 14 validation errors for Settings`  
→ **Fix**: Create `.env.development` with all 14 required env vars

**Error**: `sqlalchemy.pool.impl.NullPool` connection errors  
→ **Fix**: Start PostgreSQL, verify DATABASE_URL in `.env.development`

**Error**: `ModuleNotFoundError: No module named 'klaraflow'`  
→ **Fix**: Run `poetry install` first, use `poetry run` prefix

**Error**: Import errors on startup  
→ **Fix**: Check model import order in `models/__init__.py`

## Known Issues (see todos/todos.MD)

- TODO: Fix pydantic model parsing with multipart/form-data (`onboarding_router.py`)
- Consider merging optional/required docs models
- Collapse todo_items and onboarding_tasks
- Fix request model in `/invite` endpoint
- Inconsistent variable naming in Onboarding Module

## Development Workflow

**Making Changes**:
1. Ensure `.env.development` exists
2. Run `poetry install` after pulling changes
3. Make code changes
4. Test import: `poetry run python -c "from klaraflow import main"`
5. If models changed: `poetry run alembic revision --autogenerate -m "desc"`
6. Test server: `poetry run poe dev` (Ctrl+C to stop)
7. Test endpoints: `http://localhost:3001/docs`

**Adding Features**:
- Follow async patterns
- Add routes in `api/v1/`, CRUD in `crud/`, models in `models/`, schemas in `schemas/`
- Import models in `models/__init__.py`
- Use `APIException` for errors
- Document in `api_endpoints.md`

**Database Changes**:
1. Modify models
2. Generate migration: `poetry run alembic revision --autogenerate -m "desc"`
3. Review generated file in `alembic/versions/`
4. Test: `poetry run alembic upgrade head` then `downgrade -1`

## No CI/CD Pipeline

No GitHub Actions or automated testing configured. Before committing:
1. Test imports: `poetry run python -c "from klaraflow import main"`
2. Check for syntax errors
3. Test endpoints manually via `/docs`
4. If migrations added, test `alembic upgrade head`

## Trust These Instructions

Only search codebase if information here is incomplete, incorrect, or you need implementation details not covered. Refer to this document first before extensive exploration.

