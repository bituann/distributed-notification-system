import logging
import re
from typing import Optional

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import ObjectDoesNotExist

from template_service.exceptions import BaseException, NotFound
from template_service.models import Template
from template_service.schemas import CreateTemplate
from template_service.utils import schema_to_dict

logger = logging.getLogger(__name__)


class TemplateCacheKeys:
    """Central cache key management"""

    @staticmethod
    def template_by_id(template_id: str) -> str:
        return f"template:id:{template_id}"

    @staticmethod
    def template_latest(name: str, category: str, language: str) -> str:
        return f"template:latest:{name}:{category}:{language}"

    @staticmethod
    def template_versions(name: str, category: str, language: str) -> str:
        return f"template:versions:{name}:{category}:{language}"

    @staticmethod
    def template_list_pattern() -> str:
        return "template:list:*"

    @staticmethod
    def template_pattern_for(name: str, category: str, language: str) -> str:
        """Get pattern to invalidate all caches for a specific template"""
        return f"template:*:{name}:{category}:{language}*"


class TemplateService:
    CACHE_TIMEOUT = 3600  # 1 hour cache timeout

    @staticmethod
    def create_pagination_meta(paginator, page_obj):
        return {
            "total": paginator.count,
            "limit": paginator.per_page,
            "page": page_obj.number,
            "total_pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        }

    @classmethod
    def _invalidate_template_cache(
        cls, name: str, category: str, language: str, template_id: Optional[str] = None
    ) -> None:
        """Invalidate all caches related to a template"""
        keys_to_delete = [
            TemplateCacheKeys.template_latest(name, category, language),
            TemplateCacheKeys.template_versions(name, category, language),
        ]

        if template_id:
            keys_to_delete.append(TemplateCacheKeys.template_by_id(template_id))

        cache.delete_many(keys_to_delete)

        try:
            pattern = TemplateCacheKeys.template_list_pattern()
            cache_keys = cache.keys(pattern) if hasattr(cache, "keys") else []
            if cache_keys:
                cache.delete_many(cache_keys)
        except Exception as e:
            logger.warning(f"Could not delete pattern-based cache: {e}")

    @classmethod
    def _get_cached_template(cls, cache_key: str) -> Optional[Template]:
        """Get template from cache"""
        return cache.get(cache_key)

    @classmethod
    def _set_cached_template(cls, cache_key: str, template: Template) -> None:
        """Set template in cache"""
        cache.set(cache_key, template, cls.CACHE_TIMEOUT)

    @classmethod
    def create_template(cls, payload: CreateTemplate):
        payload_dict = schema_to_dict(payload)
        existing_template = (
            Template.objects.filter(
                name=payload.name,
                category=payload.category,
                language=payload.language,
                is_deleted=False,
            )
            .order_by("-version")
            .first()
        )
        if existing_template:
            payload_dict["version"] = existing_template.version + 1
        template = Template.objects.create(**payload_dict)
        logger.info(
            f"Template {template.name} created with ID: {template.id} version: {template.version}"
        )
        cls._invalidate_template_cache(
            template.name, template.category, template.language, template.id
        )

        return template

    @classmethod
    def update_template(cls, template_id: int, payload):
        try:
            old_template = Template.objects.get(id=template_id, is_deleted=False)
            update_payload_dict = schema_to_dict(payload)
            new_template_data = {
                "name": old_template.name,
                "category": old_template.category,
                "subject": old_template.subject,
                "body": old_template.body,
                "language": old_template.language,
                "context": old_template.context,
            }
            new_template_data.update(update_payload_dict)
            latest_template = old_template.get_latest_version()
            latest_version = (
                latest_template.version if latest_template else old_template.version
            )
            new_template_data["version"] = latest_version + 1
            new_template = Template.objects.create(**new_template_data)
            cls._invalidate_template_cache(
                new_template.name,
                new_template.category,
                new_template.language,
                template_id,
            )
            logger.info(
                f"Template {new_template.name} updated: "
                f"old version {old_template.version} (ID: {old_template.id}) -> "
                f"new version {new_template.version} (ID: {new_template.id})"
            )
            return new_template
        except Template.DoesNotExist:
            logger.error(f"Template with ID: {template_id} does not exist")
            raise NotFound(detail=f"Template with id {template_id} not found")

    @classmethod
    def get_all_templates(cls, query):
        try:
            query_dict = schema_to_dict(query)
            cache_key = (
                f"template:list:"
                f"{query_dict.get('category', 'all')}:"
                f"{query_dict.get('language', 'all')}:"
                f"page:{query_dict.get('page', 1)}:"
                f"limit:{query_dict.get('limit', 20)}"
            )
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit for template list: {cache_key}")
                return cached_result
            queryset = Template.objects.filter(is_deleted=False)
            if query_dict.get("category"):
                queryset = queryset.filter(category=query_dict["category"])
            if query_dict.get("language") is not None:
                queryset = queryset.filter(language=query_dict["language"])

            paginator = Paginator(
                queryset.order_by("-created_at"), query_dict.get("limit", 20)
            )
            page_obj = paginator.get_page(query_dict.get("page", 1))
            result = {
                "data": page_obj.object_list,
                "meta": cls.create_pagination_meta(paginator, page_obj),
                "message": "Templates retrieved successfully",
            }

            cache.set(cache_key, result, cls.CACHE_TIMEOUT // 2)
            logger.debug(f"Cached template list: {cache_key}")
            return result
        except Exception:
            return {
                "data": [],
                "meta": {
                    "total": 0,
                    "limit": 20,
                    "page": 1,
                    "total_pages": 0,
                    "has_next": False,
                    "has_previous": False,
                },
                "message": "Templates retrieved successfully",
            }

    @classmethod
    def get_template_by_id(cls, template_id):
        cache_key = TemplateCacheKeys.template_by_id(template_id)
        template = cls._get_cached_template(cache_key)
        if template:
            logger.debug(f"Cache hit for template ID: {template_id}")
            return template

        template = Template.objects.filter(id=template_id, is_deleted=False).first()
        if template:
            cls._set_cached_template(cache_key, template)
            logger.debug(f"Cached template ID: {template_id}")
        return template

    @classmethod
    def get_latest_template(cls, name, category, language):
        cache_key = TemplateCacheKeys.template_latest(name, category, language)
        cached_template = cls._get_cached_template(cache_key)
        if cached_template:
            logger.debug(f"Cache hit for latest template: {name}/{category}/{language}")
            return cached_template
        template = (
            Template.objects.filter(
                name=name,
                category=category,
                language=language,
                is_deleted=False,
                is_active=True,
            )
            .order_by("-version")
            .first()
        )

        if not template:
            logger.warning(f"No active template found for {name}/{category}/{language}")
            raise ValueError(f"Template '{name}' ({category}, {language}) not found")

        cls._set_cached_template(cache_key, template)
        logger.debug(f"Cached latest template: {name}/{category}/{language}")

        return template

    @classmethod
    def render_template(cls, payload):
        try:
            if payload.id:
                try:
                    template = Template.objects.get(id=payload.id, is_deleted=False)
                except (ValueError, ObjectDoesNotExist):
                    raise ValueError(f"Template with ID '{payload.id}' not found")
            elif payload.name:
                template = cls.get_latest_template(
                    name=payload.name,
                    category=payload.category,
                    language=payload.language,
                )
            else:
                raise ValueError("Either 'id' or 'name' must be provided")

            required_vars = set(template.context) if template.context else set()
            provided_vars = set(payload.context.keys())
            missing_vars = required_vars - provided_vars
            if missing_vars:
                raise BaseException(
                    message="Missing required context variables",
                    detail=f"Missing required context variables: {', '.join(sorted(missing_vars))}",
                    status_code=400,
                )

            rendered_subject = cls._replace_variables(
                template.subject or "", payload.context
            )
            rendered_body = cls._replace_variables(template.body, payload.context)

            logger.info(
                f"Template '{template.name}' (v{template.version}) rendered successfully"
            )

            return {
                "template_id": str(template.id),
                "template_name": template.name,
                "version": template.version,
                "category": template.category,
                "language": template.language,
                "subject": rendered_subject,
                "body": rendered_body,
            }

        except Exception as e:
            raise BaseException(
                message="Template rendering failed", detail=str(e), status_code=400
            )

    @staticmethod
    def _replace_variables(text: str, context: dict) -> str:
        """
        Replace {{variable}} placeholders with values from context

        Args:
            text: Text containing {{variable}} placeholders
            context: Dictionary of variable values

        Returns:
            Text with variables replaced
        """

        def replace_match(match):
            var_name = match.group(1)
            return str(context.get(var_name, match.group(0)))

        pattern = r"\{\{(\w+)\}\}"
        return re.sub(pattern, replace_match, text)

    @classmethod
    def delete_template(cls, template_id):
        try:
            template = Template.objects.get(id=template_id, is_deleted=False)
            template.is_deleted = True
            template.save(update_fields=["is_deleted", "updated_at"])
            cls._invalidate_template_cache(
                template.name, template.category, template.language, template_id
            )

            logger.info(f"Template '{template.name}' (ID: {template_id}) soft deleted")
        except Template.DoesNotExist:
            raise NotFound(detail=f"Template with id {template_id} not found")

    @classmethod
    def permanently_delete_template(cls, template_id):
        try:
            template = Template.objects.get(id=template_id)
            name = template.name
            category = template.category
            language = template.language

            template.delete()

            cls._invalidate_template_cache(name, category, language, template_id)

            logger.info(f"Template '{name}' (ID: {template_id}) permanently deleted")
        except Template.DoesNotExist:
            raise NotFound(detail=f"Template with id {template_id} not found")
