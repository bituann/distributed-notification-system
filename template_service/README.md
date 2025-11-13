# Template Service

A Django-based template management service for distributed notification systems. This service provides RESTful APIs for creating, managing, and rendering templates with support for multiple languages, categories, and versioning.

## Features

- **Template Management**: Create, update, retrieve, and delete templates
- **Multi-language Support**: Templates can be created in different languages
- **Versioning**: Automatic version control for template updates
- **Caching**: Redis-based caching for improved performance
- **Template Rendering**: Dynamic template rendering with context variables
- **Categories**: Support for email and push notification templates
- **Pagination**: Efficient pagination for template listings
- **Soft Delete**: Templates are soft deleted for data integrity

## Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL
- Redis
- UV (recommended) or pip

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Django Configuration
SECRET_KEY=your_secret_key_here
DEBUG=True

# Additional Configuration
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Installation with UV (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd template_service
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Run database migrations**
   ```bash
   make migrate
   ```

4. **Create a superuser (optional)**
   ```bash
   uv run python manage.py createsuperuser
   ```

5. **Run the development server**
   ```bash
   make run
   ```

### Installation with pip

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd template_service
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   make run
   ```

Once development server is running, access the API documentation at:

```http
http://localhost:8000/api/docs/
```

## API Endpoints

### 1. Create Template
- **Endpoint**: `POST /api/v1/template-service/templates`
- **Description**: Creates a new template

**Request Body Example:**
```json
{
  "name": "welcome_email",
  "category": "email",
  "subject": "Welcome {{user_name}}!",
  "body": "Hello {{user_name}},\n\nWelcome to our platform! Your account has been created successfully.\n\nBest regards,\n{{company_name}}",
  "language": "en",
  "context": ["user_name", "company_name"]
}
```

**Response Example:**
```json
{
  "success": true,
  "message": "Template created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "welcome_email",
    "category": "email",
    "subject": "Welcome {{user_name}}!",
    "body": "Hello {{user_name}},\n\nWelcome to our platform! Your account has been created successfully.\n\nBest regards,\n{{company_name}}",
    "language": "en",
    "version": 1,
    "context": ["user_name", "company_name"],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 2. Update Template
- **Endpoint**: `PATCH /api/v1/template-service/templates/{template_id}`
- **Description**: Updates an existing template (creates new version)

**Request Body Example:**
```json
{
  "subject": "Updated Welcome {{user_name}}!",
  "body": "Hello {{user_name}},\n\nWelcome to our updated platform! Your account has been created successfully.\n\nBest regards,\n{{company_name}}"
}
```

**Response Example:**
```json
{
  "message": "Template updated successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "welcome_email",
    "category": "email",
    "subject": "Updated Welcome {{user_name}}!",
    "body": "Hello {{user_name}},\n\nWelcome to our updated platform! Your account has been created successfully.\n\nBest regards,\n{{company_name}}",
    "language": "en",
    "version": 2,
    "context": ["user_name", "company_name"],
    "created_at": "2024-01-15T11:00:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

### 3. Get All Templates
- **Endpoint**: `GET /api/v1/template-service/templates`
- **Description**: Retrieves paginated list of templates with optional filtering

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)
- `category` (optional): Filter by category (email/push)
- `language` (optional): Filter by language code

**Example Request:**
```bash
GET /api/v1/template-service/templates?page=1&limit=10&category=email&language=en
```

**Response Example:**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "welcome_email",
      "category": "email",
      "subject": "Welcome {{user_name}}!",
      "body": "Hello {{user_name}},\n\nWelcome to our platform! Your account has been created successfully.\n\nBest regards,\n{{company_name}}",
      "language": "en",
      "version": 1,
      "context": ["user_name", "company_name"],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "meta": {
    "total": 1,
    "limit": 10,
    "page": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  },
  "message": "Templates retrieved successfully"
}
```

### 4. Get Template by ID
- **Endpoint**: `GET /api/v1/template-service/templates/{template_id}`
- **Description**: Retrieves a specific template by its ID

**Example Request:**
```bash
GET /api/v1/template-service/templates/550e8400-e29b-41d4-a716-446655440000
```

**Response Example:**
```json
{
  "message": "Template retrieved successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "welcome_email",
    "category": "email",
    "subject": "Welcome {{user_name}}!",
    "body": "Hello {{user_name}},\n\nWelcome to our platform! Your account has been created successfully.\n\nBest regards,\n{{company_name}}",
    "language": "en",
    "version": 1,
    "context": ["user_name", "company_name"],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 5. Render Template
- **Endpoint**: `POST /api/v1/template-service/templates/render`
- **Description**: Renders a template with provided context variables

**Request Body Example (by template name):**
```json
{
  "name": "welcome_email",
  "category": "email",
  "language": "en",
  "context": {
    "user_name": "John Doe",
    "company_name": "Acme Corp"
  }
}
```

**Request Body Example (by template ID):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "context": {
    "user_name": "John Doe",
    "company_name": "Acme Corp"
  }
}
```

**Response Example:**
```json
{
  "message": "Template rendered successfully",
  "data": {
    "template_id": "550e8400-e29b-41d4-a716-446655440000",
    "template_name": "welcome_email",
    "version": 1,
    "category": "email",
    "language": "en",
    "subject": "Welcome John Doe!",
    "body": "Hello John Doe,\n\nWelcome to our platform! Your account has been created successfully.\n\nBest regards,\nAcme Corp"
  }
}
```

### 6. Delete Template
- **Endpoint**: `DELETE /api/v1/template-service/templates/{template_id}`
- **Description**: Soft deletes a template

**Example Request:**
```bash
DELETE /api/v1/template-service/templates/550e8400-e29b-41d4-a716-446655440000
```

**Response Example:**
```json
{
  "success": true,
  "message": "Template deleted successfully"
}
```

## Development

### Running Tests

```bash
# With UV
uv run pytest

# With pip
pytest
```

### Code Quality

```bash
# Linting
uv run ruff check .

# Formatting
uv run ruff format .
```

### Database Migrations

```bash
# Create new migration
uv run python manage.py makemigrations

# Apply migrations
uv run python manage.py migrate
```
