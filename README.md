# Localization Management API

FastAPI backend for managing translation keys and localized content with Supabase PostgreSQL.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Supabase account and project
- PostgreSQL database (via Supabase)

### Installation

1. **Clone and setup:**

   ```bash
   cd localization-management-api
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Setup:**
   Create a `.env` file in the root directory:

   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_SERVICE_KEY=your_supabase_service_role_key
   API_HOST=localhost
   API_PORT=8000
   DEBUG=true
   FRONTEND_URL=http://localhost:3000
   ```

3. **Run the server:**

   ```bash
   python run_server.py
   ```

   Or using uvicorn directly:

   ```bash
   uvicorn src.localization_management_api.main:app --reload
   ```

## 📚 API Endpoints

### Projects

- `GET /projects` - Get all projects with languages

### Translation Keys

- `GET /projects/{project_id}/translation-keys` - Get translation keys with filtering
  - Query params: `page`, `limit`, `search`, `category`, `language_code`, `missing_translations`
- `GET /translation-keys/{key_id}` - Get single translation key
- `POST /translation-keys` - Create new translation key

### Translations

- `POST /translations` - **NEW** Create individual translation
- `PUT /translations/{key_id}/{language_code}` - Update/create translation
- `POST /translations/bulk-update` - Bulk update multiple translations

### Analytics

- `GET /projects/{project_id}/analytics` - Get translation completion analytics

### Legacy

- `GET /localizations/{project_id}/{locale}` - Get flat key-value translations

## 🆕 New Translation Creation Endpoint

### `POST /translations`

Create a new translation for an existing translation key.

**Request Body:**

```json
{
  "key_id": "uuid-of-translation-key",
  "language_code": "es",
  "value": "Hola Mundo",
  "updated_by": "user@example.com"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Translation created successfully",
  "key_id": "uuid-of-translation-key",
  "language_code": "es"
}
```

**Error Cases:**

- `404` - Translation key not found
- `409` - Translation already exists (use PUT to update)
- `400` - Validation or creation error

## 🔄 How It Works

### Creating Translations (2 Ways)

1. **With Translation Key** (Recommended):

   ```http
   POST /translation-keys
   {
     "key": "button.save",
     "category": "buttons",
     "project_id": "project-uuid",
     "initial_translations": {
       "en": "Save",
       "es": "Guardar"
     }
   }
   ```

2. **Individual Translation** (For existing keys):
   ```http
   POST /translations
   {
     "key_id": "existing-key-uuid",
     "language_code": "fr",
     "value": "Sauvegarder"
   }
   ```

### Updating Translations

```http
PUT /translations/{key_id}/{language_code}
{
  "value": "Updated translation"
}
```

## 🗄️ Database Schema

The API works with these Supabase tables:

- `projects` - Project information
- `languages` - Available languages
- `project_languages` - Language assignments to projects
- `translation_keys` - Translation key definitions
- `translations` - Actual translation values

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src
```

## 🌐 CORS Configuration

The API is configured for cross-origin requests from:

- `http://localhost:3000` (Next.js frontend)
- Environment-configured frontend URL

## 📝 API Documentation

When running the server, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Features

- ✅ Full CRUD operations for translation keys
- ✅ Individual and bulk translation updates
- ✅ **NEW** Dedicated translation creation endpoint
- ✅ Advanced filtering and search
- ✅ Translation completion analytics
- ✅ Supabase integration
- ✅ Type-safe with Pydantic models
- ✅ Comprehensive error handling
- ✅ CORS enabled for frontend integration
