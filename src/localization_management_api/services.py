from typing import List, Dict, Optional, Tuple
from datetime import datetime
from .database import supabase
from .models import TranslationKey, Translation, Language, Project
import uuid

class TranslationService:

    async def get_translation_keys(
        self,
        project_id: str,
        page: int = 1,
        limit: int = 50,
        search: Optional[str] = None,
        category: Optional[str] = None,
        language_code: Optional[str] = None,
        missing_translations: Optional[bool] = None
    ) -> Tuple[List[TranslationKey], int]:
        """Get translation keys with optional filtering"""

        # Build query
        query = supabase.table("translation_keys").select(
            """
            id, key, category, description, created_at, updated_at,
            translations(language_code, value, updated_at, updated_by)
            """
        ).eq("project_id", project_id)

        # Apply filters
        if search:
            query = query.ilike("key", f"%{search}%")
        if category:
            query = query.eq("category", category)

        # Get all filtered data first to apply missing translations filter and calculate correct count
        result = query.execute()

        # Transform data and apply missing translations filter
        filtered_translation_keys = []
        for row in result.data:
            translations = {}
            for trans in row.get("translations", []):
                translations[trans["language_code"]] = Translation(
                    value=trans["value"],
                    updated_at=datetime.fromisoformat(trans["updated_at"].replace("Z", "+00:00")),
                    updated_by=trans["updated_by"]
                )

            # Apply missing translations filter if requested
            if missing_translations:
                if language_code:
                    # Show only keys that are MISSING the specified language translation
                    translation = translations.get(language_code)
                    if translation and translation.value and translation.value.strip():
                        continue  # Skip keys that have a valid translation for this language
                else:
                    # Show only keys that are missing translations for ANY language
                    # Get all languages for this project first
                    project_languages_result = supabase.table("project_languages").select("language_code").eq("project_id", project_id).execute()
                    project_language_codes = [lang["language_code"] for lang in project_languages_result.data]

                    # Check if this key has translations for all project languages
                    has_all_translations = True
                    for lang_code in project_language_codes:
                        translation = translations.get(lang_code)
                        if not translation or not translation.value or not translation.value.strip():
                            has_all_translations = False
                            break

                    if has_all_translations:
                        continue  # Skip keys that have all translations

            translation_key = TranslationKey(
                id=row["id"],
                key=row["key"],
                category=row["category"],
                description=row.get("description"),
                translations=translations
            )
            filtered_translation_keys.append(translation_key)

        # Calculate total after all filters are applied
        total = len(filtered_translation_keys)

        # Apply pagination to the filtered results
        offset = (page - 1) * limit
        paginated_keys = filtered_translation_keys[offset:offset + limit]

        return paginated_keys, total

    async def get_translation_key_by_id(self, key_id: str) -> Optional[TranslationKey]:
        """Get a single translation key by ID"""
        result = supabase.table("translation_keys").select(
            """
            id, key, category, description, created_at, updated_at,
            translations(language_code, value, updated_at, updated_by)
            """
        ).eq("id", key_id).execute()

        if not result.data:
            return None

        row = result.data[0]
        translations = {}
        for trans in row.get("translations", []):
            translations[trans["language_code"]] = Translation(
                value=trans["value"],
                updated_at=datetime.fromisoformat(trans["updated_at"].replace("Z", "+00:00")),
                updated_by=trans["updated_by"]
            )

        return TranslationKey(
            id=row["id"],
            key=row["key"],
            category=row["category"],
            description=row.get("description"),
            translations=translations
        )

    async def create_translation_key(
        self,
        key: str,
        category: str,
        project_id: str,
        description: Optional[str] = None,
        initial_translations: Optional[Dict[str, str]] = None
    ) -> TranslationKey:
        """Create a new translation key"""
        key_id = str(uuid.uuid4())

        # Insert translation key
        key_data = {
            "id": key_id,
            "key": key,
            "category": category,
            "project_id": project_id,
            "description": description
        }

        supabase.table("translation_keys").insert(key_data).execute()

        # Insert initial translations if provided
        if initial_translations:
            translation_data = []
            for lang_code, value in initial_translations.items():
                translation_data.append({
                    "id": str(uuid.uuid4()),
                    "translation_key_id": key_id,
                    "language_code": lang_code,
                    "value": value,
                    "updated_by": "system"
                })

            if translation_data:
                supabase.table("translations").insert(translation_data).execute()

        # Return the created key
        return await self.get_translation_key_by_id(key_id)

    async def update_translation(
        self,
        key_id: str,
        language_code: str,
        value: str,
        updated_by: str = "system"
    ) -> bool:
        """Update a translation value"""

        # Check if translation exists
        existing = supabase.table("translations").select("id").eq("translation_key_id", key_id).eq("language_code", language_code).execute()

        if existing.data:
            # Update existing translation
            supabase.table("translations").update({
                "value": value,
                "updated_by": updated_by
            }).eq("translation_key_id", key_id).eq("language_code", language_code).execute()
        else:
            # Create new translation
            supabase.table("translations").insert({
                "id": str(uuid.uuid4()),
                "translation_key_id": key_id,
                "language_code": language_code,
                "value": value,
                "updated_by": updated_by
            }).execute()

        return True

    async def bulk_update_translations(self, updates: List[Dict]) -> int:
        """Bulk update multiple translations"""
        success_count = 0

        for update in updates:
            try:
                await self.update_translation(
                    update["key_id"],
                    update["language_code"],
                    update["value"],
                    update.get("updated_by", "system")
                )
                success_count += 1
            except Exception as e:
                # Log error but continue with other updates
                print(f"Failed to update translation: {e}")
                continue

        return success_count

    async def delete_translation_key(self, key_id: str) -> bool:
        """Delete a translation key and all its associated translations"""
        try:
            # Check if translation key exists
            existing_key = await self.get_translation_key_by_id(key_id)
            if not existing_key:
                return False

            # Delete all translations for this key first (due to foreign key constraints)
            supabase.table("translations").delete().eq("translation_key_id", key_id).execute()

            # Delete the translation key
            result = supabase.table("translation_keys").delete().eq("id", key_id).execute()

            return len(result.data) > 0
        except Exception as e:
            print(f"Failed to delete translation key: {e}")
            return False

    async def get_projects(self) -> List[Project]:
        """Get all projects with their languages"""
        result = supabase.table("projects").select(
            """
            id, name, description, created_at, updated_at,
            project_languages(language_code, languages(code, name, flag))
            """
        ).execute()

        projects = []
        for row in result.data:
            languages = []
            for pl in row.get("project_languages", []):
                lang_data = pl["languages"]
                languages.append(Language(
                    code=lang_data["code"],
                    name=lang_data["name"],
                    flag=lang_data.get("flag")
                ))

            projects.append(Project(
                id=row["id"],
                name=row["name"],
                description=row.get("description"),
                languages=languages,
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
            ))

        return projects

    async def get_analytics(self, project_id: str) -> Dict:
        """Get analytics for translation completion"""

        # Get total keys
        keys_result = supabase.table("translation_keys").select("id", count="exact").eq("project_id", project_id).execute()
        total_keys = keys_result.count if keys_result.count else 0

        # Get completion by language
        languages_result = supabase.table("project_languages").select("language_code").eq("project_id", project_id).execute()

        completion_by_language = {}
        for lang_row in languages_result.data:
            lang_code = lang_row["language_code"]

            # Count translations for this language
            trans_result = supabase.table("translations").select(
                "id", count="exact"
            ).eq("language_code", lang_code).execute()

            completed = trans_result.count if trans_result.count else 0

            completion_by_language[lang_code] = {
                "completed": completed,
                "total": total_keys,
                "percentage": round((completed / total_keys * 100) if total_keys > 0 else 0, 2)
            }

        return {
            "project_id": project_id,
            "total_keys": total_keys,
            "completion_by_language": completion_by_language,
            "last_updated": datetime.utcnow()
        }