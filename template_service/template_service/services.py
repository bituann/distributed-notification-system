import logging
import re

from django.core.paginator import Paginator
from django.db.models import ObjectDoesNotExist

from template_service.exceptions import BaseException, NotFound
from template_service.models import Template
from template_service.schemas import CreateTemplate
from template_service.utils import schema_to_dict

logger = logging.getLogger(__name__)


class TemplateService:
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
        logger.info(f"Template {template.name} created with ID: {template.id}")
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
            queryset = Template.objects.filter(is_deleted=False)
            if query_dict.get("category"):
                queryset = queryset.filter(category=query_dict["category"])
            if query_dict.get("language") is not None:
                queryset = queryset.filter(language=query_dict["language"])

            paginator = Paginator(
                queryset.order_by("-created_at"), query_dict.get("limit", 20)
            )
            page_obj = paginator.get_page(query_dict.get("page", 1))
            return {
                "data": page_obj.object_list,
                "meta": cls.create_pagination_meta(paginator, page_obj),
            }
        except Exception:
            return {}

    @classmethod
    def get_template_by_id(cls, template_id):
        template = Template.objects.filter(id=template_id).first()
        return template

    @classmethod
    def get_latest_template(cls, name, category, language):
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
