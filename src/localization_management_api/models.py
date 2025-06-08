from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class Translation(BaseModel):
    value: str
    updated_at: datetime
    updated_by: str

class TranslationKey(BaseModel):
    id: str
    key: str
    category: str
    description: Optional[str] = None
    translations: Dict[str, Translation]

class Language(BaseModel):
    code: str
    name: str
    flag: Optional[str] = None

class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    languages: List[Language]
    created_at: datetime
    updated_at: datetime

class GetTranslationKeysResponse(BaseModel):
    keys: List[TranslationKey]
    total: int
    page: int
    limit: int

class CreateTranslationKeyRequest(BaseModel):
    key: str
    category: str
    description: Optional[str] = None
    project_id: str = Field(alias="projectId")
    initial_translations: Optional[Dict[str, str]] = Field(default=None, alias="initialTranslations")

class UpdateTranslationRequest(BaseModel):
    key_id: str
    language_code: str
    value: str

class CreateTranslationRequest(BaseModel):
    key_id: str
    language_code: str
    value: str
    updated_by: Optional[str] = "api_user"

class BulkUpdateRequest(BaseModel):
    updates: List[UpdateTranslationRequest]

class ValidationError(BaseModel):
    key_id: str
    language_code: str
    error: str
    suggestion: Optional[str] = None

class ValidationResponse(BaseModel):
    is_valid: bool
    errors: List[ValidationError]

class AnalyticsResponse(BaseModel):
    project_id: str
    total_keys: int
    completion_by_language: Dict[str, Dict[str, int]]
    last_updated: datetime