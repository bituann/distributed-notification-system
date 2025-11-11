import logging

from template_service.exceptions import NotFound
from template_service.models import Template
from template_service.schemas import CreateTemplate
from template_service.utils import schema_to_dict

logger = logging.getLogger(__name__)


class TemplateService:
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
            new_template_data["version"] = old_template.get_latest_version() + 1
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
