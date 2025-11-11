from ninja import Router

from template_service.schemas import (
    CreateTemplate,
    ErrorResponse,
    TemapleteDataResponse,
    UpdateTemplate,
)
from template_service.services import TemplateService

router = Router()


@router.post("/templates", response={201: TemapleteDataResponse, 400: ErrorResponse})
def create_template(request, payload: CreateTemplate):
    try:
        template = TemplateService.create_template(payload)
        return 201, {
            "success": True,
            "message": "Template created successfully",
            "data": template,
        }
    except Exception as e:
        return 400, {"success": False, "message": str(e)}


@router.patch(
    "/templates/{template_id}",
    response={200: TemapleteDataResponse},
)
def update_template(request, template_id: str, payload: UpdateTemplate):
    template = TemplateService.update_template(template_id, payload)
    return 200, {
        "message": "Template updated successfully",
        "data": template,
    }
