# KlaraFlow API Endpoints

This document lists all API endpoints from the authentication, onboarding, and main application routers for easier frontend integration.

## Authentication Routes (`/api/v1/auth`)

### POST `/api/v1/auth/signup`
**Description**: Create a new user account.  
**What to send**: UserCreate schema with email, password, and other user details.  
**What to expect**: UserPublic schema with created user information.  
**When to use**: During user registration process.  
**Backend action**: Creates new user record in database with hashed password.

### POST `/api/v1/auth/login`
**Description**: Authenticate user and return access token.  
**What to send**: UserLogin schema with email and password.  
**What to expect**: Response with access token and expiration time.  
**When to use**: When user logs into the application.  
**Backend action**: Verifies credentials against database, generates JWT token.

### POST `/api/v1/auth/activate`
**Description**: Activate employee account using onboarding invitation token.  
**What to send**: OnboardingActivationRequest with invitation token and new password.  
**What to expect**: Access token for immediate login after activation.  
**When to use**: After receiving onboarding invitation email, to set password and activate account.  
**Backend action**: Validates token, creates permanent user record, marks onboarding session as in-progress.

## Onboarding Routes (`/api/v1/onboarding`)

### POST `/api/v1/onboarding/invite`
**Description**: Admin endpoint to invite new employee with optional profile picture upload.  
**What to send**: Multipart form data with employee details (empId, firstName, etc.) and optional profilePic file.  
**What to expect**: OnboardingSessionRead schema with created session details.  
**When to use**: When admin wants to invite a new employee to start onboarding process.  
**Backend action**: Creates onboarding session record, uploads profile picture to S3, sends invitation email.

### GET `/api/v1/onboarding/session/{token}`
**Description**: Retrieve onboarding session data using invitation token.  
**What to send**: Token as URL parameter.  
**What to expect**: OnboardingSessionDataResponse with session information.  
**When to use**: When employee clicks invitation link to view onboarding details.  
**Backend action**: Validates token and returns session data from database.

### GET `/api/v1/onboarding/session/status/{token}`
**Description**: Get current status and step of onboarding session.  
**What to send**: Token as URL parameter.  
**What to expect**: Object with status and current_step fields.  
**When to use**: To check progress of onboarding session.  
**Backend action**: Retrieves status and step from onboarding session record.

### PUT `/api/v1/onboarding/session/step/{token}`
**Description**: Update the current step of an onboarding session.  
**What to send**: Token as URL parameter, OnboardingStepUpdateRequest with current_step.  
**What to expect**: Updated OnboardingSessionRead schema.  
**When to use**: When employee progresses through onboarding steps.  
**Backend action**: Updates current_step field in onboarding session record.

### GET `/api/v1/onboarding/my-data`
**Description**: Get current user's onboarding data including todos and documents.  
**What to send**: Authorization header with user token.  
**What to expect**: OnboardingDataRead schema with session data, todos, and document requirements.  
**When to use**: When authenticated user wants to view their onboarding progress and tasks.  
**Backend action**: Retrieves user's active onboarding session and associated template data.

### PUT `/api/v1/onboarding/step`
**Description**: Update current user's onboarding step.  
**What to send**: OnboardingStepUpdateRequest with current_step, authorization header.  
**What to expect**: Updated OnboardingDataRead schema.  
**When to use**: When user advances to next onboarding step.  
**Backend action**: Updates current_step in user's onboarding session record.

### PUT `/api/v1/onboarding/todos/{todo_id}`
**Description**: Mark a specific todo item as completed or incomplete.  
**What to send**: todo_id as URL parameter, completed boolean in request body, authorization header.  
**What to expect**: Success response with message.  
**When to use**: When user completes or uncompletes a todo item during onboarding.  
**Backend action**: Updates is_completed field in OnboardingTask record.

### POST `/api/v1/onboarding/submit`
**Description**: Submit onboarding process as completed.  
**What to send**: Authorization header.  
**What to expect**: Success response confirming completion.  
**When to use**: When user finishes all onboarding requirements and submits.  
**Backend action**: Marks onboarding session as completed, activates user account.

### PUT `/api/v1/onboarding/my-data`
**Description**: Update current user's onboarding data.  
**What to send**: Dictionary of employee data fields to update, authorization header.  
**What to expect**: Updated OnboardingDataRead schema.  
**When to use**: When user updates their personal information during onboarding.  
**Backend action**: Updates corresponding fields in onboarding session record.

### POST `/api/v1/onboarding/documents/upload`
**Description**: Upload a document for onboarding requirements.  
**What to send**: Multipart form with document_template_id and file, authorization header.  
**What to expect**: Response with uploaded file URL.  
**When to use**: When user needs to upload required or optional documents during onboarding.  
**Backend action**: Uploads file to S3, creates OnboardingDocument record linking to session.

## Main Application Routes

### GET `/`
**Description**: Welcome endpoint for the API.  
**What to send**: Nothing.  
**What to expect**: Simple message indicating API is running.  
**When to use**: For basic health check or API discovery.  
**Backend action**: Returns static response, no database interaction.

### GET `/health`
**Description**: Check database connectivity and API health.  
**What to send**: Nothing.  
**What to expect**: Health status with database connection info.  
**When to use**: For monitoring API and database availability.  
**Backend action**: Executes simple database query to verify connection.