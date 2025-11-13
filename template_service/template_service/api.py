from ninja import Query, Router

from template_service.schemas import (
    CreateTemplate,
    ErrorResponse,
    RenderedTemplateResponse,
    RenderTemplateRequest,
    TemapleteDataResponse,
    TemplateListResponse,
    TemplatesQuerySchema,
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


@router.post(
    "templates/render", response={200: RenderedTemplateResponse, 400: ErrorResponse}
)
def render_template(request, payload: RenderTemplateRequest):
    try:
        data = TemplateService.render_template(payload)
        return {"message": "Template rendered successfully", "data": data}
    except Exception as e:
        return 400, {"success": False, "message": str(e)}


@router.patch(
    "/templates/{template_id}",
    response={200: TemapleteDataResponse, 404: ErrorResponse},
)
def update_template(request, template_id: str, payload: UpdateTemplate):
    try:
        template = TemplateService.update_template(template_id, payload)
        return 200, {
            "message": "Template updated successfully",
            "data": template,
        }
    except Exception as e:
        return 404, {"success": False, "message": str(e)}


@router.get("/templates", response={200: TemplateListResponse})
def get_all_templates(request, query: Query[TemplatesQuerySchema]):
    data = TemplateService.get_all_templates(query)
    data["message"] = "Templates retrieved successfully"
    return data


@router.get(
    "/templates/{template_id}",
    response={200: TemapleteDataResponse, 404: ErrorResponse},
)
def get_template_by_id(request, template_id: str):
    template = TemplateService.get_template_by_id(template_id)
    if not template:
        return 404, {
            "success": False,
            "message": f"Template with id {template_id} not found",
        }
    return {
        "message": "Template retrieved successfully",
        "data": template,
    }


@router.delete("/templates/{template_id}", response={200: dict, 404: ErrorResponse})
def delete_template(request, template_id: str):
    try:
        TemplateService.delete_template(template_id)
        return {"success": True, "message": "Template deleted successfully"}
    except Exception as e:
        return 404, {"success": False, "message": str(e)}
