from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from .config import get_settings
from .services import TranslationService
from .models import (
    TranslationKey, GetTranslationKeysResponse, CreateTranslationKeyRequest,
    UpdateTranslationRequest, BulkUpdateRequest, AnalyticsResponse, Project, Language
)

# Initialize FastAPI app
app = FastAPI(
    title="Localization Management API",
    description="API for managing translation keys and localized content",
    version="1.0.0"
)

# Settings
settings = get_settings()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
translation_service = TranslationService()

# Dependency to get translation service
def get_translation_service() -> TranslationService:
    return translation_service

@app.get("/")
async def root():
    return {"message": "Localization Management API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# Projects endpoints
@app.get("/projects", response_model=List[Project])
async def get_projects(service: TranslationService = Depends(get_translation_service)):
    """Get all projects with their languages"""
    return await service.get_projects()

# Translation Keys endpoints
@app.get("/projects/{project_id}/translation-keys", response_model=GetTranslationKeysResponse)
async def get_translation_keys(
    project_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    language_code: Optional[str] = Query(None),
    missing_translations: Optional[bool] = Query(None),
    service: TranslationService = Depends(get_translation_service)
):
    """Get translation keys for a project with optional filtering"""
    try:
        keys, total = await service.get_translation_keys(
            project_id=project_id,
            page=page,
            limit=limit,
            search=search,
            category=category,
            language_code=language_code,
            missing_translations=missing_translations
        )

        return GetTranslationKeysResponse(
            keys=keys,
            total=total,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch translation keys: {str(e)}")

@app.get("/translation-keys/{key_id}", response_model=TranslationKey)
async def get_translation_key(
    key_id: str,
    service: TranslationService = Depends(get_translation_service)
):
    """Get a single translation key by ID"""
    key = await service.get_translation_key_by_id(key_id)
    if not key:
        raise HTTPException(status_code=404, detail="Translation key not found")
    return key

@app.post("/translation-keys", response_model=TranslationKey)
async def create_translation_key(
    request: CreateTranslationKeyRequest,
    service: TranslationService = Depends(get_translation_service)
):
    """Create a new translation key"""
    try:
        return await service.create_translation_key(
            key=request.key,
            category=request.category,
            project_id=request.project_id,
            description=request.description,
            initial_translations=request.initial_translations
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create translation key: {str(e)}")

@app.put("/translations/{key_id}/{language_code}")
async def update_translation(
    key_id: str,
    language_code: str,
    request: UpdateTranslationRequest,
    service: TranslationService = Depends(get_translation_service)
):
    """Update a translation value"""
    try:
        success = await service.update_translation(
            key_id=key_id,
            language_code=language_code,
            value=request.value,
            updated_by="api_user"
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update translation")
        return {"success": True, "message": "Translation updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update translation: {str(e)}")

@app.post("/translations/bulk-update")
async def bulk_update_translations(
    request: BulkUpdateRequest,
    service: TranslationService = Depends(get_translation_service)
):
    """Bulk update multiple translations"""
    try:
        updates = [
            {
                "key_id": update.key_id,
                "language_code": update.language_code,
                "value": update.value,
                "updated_by": "api_user"
            }
            for update in request.updates
        ]

        success_count = await service.bulk_update_translations(updates)
        return {
            "success": True,
            "message": f"Updated {success_count} out of {len(request.updates)} translations",
            "updated_count": success_count,
            "total_requested": len(request.updates)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to bulk update translations: {str(e)}")

@app.get("/projects/{project_id}/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    project_id: str,
    service: TranslationService = Depends(get_translation_service)
):
    """Get analytics for translation completion"""
    try:
        analytics = await service.get_analytics(project_id)
        return AnalyticsResponse(**analytics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")

# Legacy endpoint (from original requirement)
@app.get("/localizations/{project_id}/{locale}")
async def get_localizations(
    project_id: str,
    locale: str,
    service: TranslationService = Depends(get_translation_service)
):
    """Legacy endpoint for getting localizations for a project and locale"""
    try:
        keys, _ = await service.get_translation_keys(project_id=project_id, limit=1000)

        localizations = {}
        for key in keys:
            if locale in key.translations:
                localizations[key.key] = key.translations[locale].value

        return {
            "project_id": project_id,
            "locale": locale,
            "localizations": localizations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch localizations: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port, reload=settings.debug)
