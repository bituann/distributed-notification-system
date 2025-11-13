from enum import Enum
from typing import Generic, List, Optional, TypeVar

from ninja import Field, ModelSchema, Schema
from pydantic import model_validator

from template_service.models import Template

T = TypeVar("T", bound=Schema)


class ApiResponse(Schema):
    success: bool = Field(True, description="Indicates if the API call was successful")
    message: Optional[str] = Field(
        ..., description="A message providing additional information"
    )


class ErrorResponse(ApiResponse):
    success: bool = Field(False, description="Indicates if the API call was successful")
    error: Optional[dict] = Field(None, description="Details about the error")


class ApiResponseData(ApiResponse, Generic[T]):
    data: Optional[T] = Field(None, description="The data returned by the API")


class TemplateCategory(str, Enum):
    EMAIL = "email"
    PUSH = "push"


class CreateTemplate(Schema):
    name: str = Field(
        ..., min_length=1, max_length=255, description="The name of the template"
    )
    category: TemplateCategory = Field(..., description="The category of the template")
    subject: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="The subject of the template (if applicable)",
    )
    body: str = Field(..., description="The body of the template")
    language: Optional[str] = Field(
        "en",
        description="The language code of the template",
        examples=["en", "fr"],
    )
    context: Optional[List] = Field(
        None, description="The context variables for the template"
    )


class UpdateTemplate(Schema):
    name: Optional[str] = Field(None, description="The name of the template")
    category: Optional[TemplateCategory] = None
    subject: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="The subject of the template (if applicable)",
    )

    body: Optional[str] = Field(None, description="The body of the template")
    language: Optional[str] = Field(
        None,
        description="The language code of the template",
        examples=["en", "fr"],
    )
    context: Optional[List] = Field(
        None, description="The context variables for the template"
    )


class TemplateResponse(ModelSchema):
    class Meta:
        model = Template
        fields = [
            "id",
            "name",
            "category",
            "subject",
            "body",
            "language",
            "version",
            "context",
            "created_at",
            "updated_at",
        ]


class TemapleteDataResponse(ApiResponseData[TemplateResponse]):
    pass


class TemplatesQuerySchema(Schema):
    page: Optional[int] = Field(1, ge=1, description="Page number for pagination")
    limit: Optional[int] = Field(
        20, ge=1, le=100, description="Number of items per page"
    )
    category: Optional[TemplateCategory] = Field(
        None, description="Filter templates by category"
    )
    language: Optional[str] = Field(
        None, description="Filter templates by language code", examples=["en", "fr"]
    )


class PaginationMeta(Schema):
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Total number of pages")
    page: int = Field(..., description="Current page number")
    total_pages: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Indicates if there is a next page")
    has_previous: bool = Field(..., description="Indicates if there is a previous page")


class TemplateListResponse(ApiResponse):
    data: List[TemplateResponse] = Field(..., description="List of templates")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class RenderTemplateRequest(Schema):
    id: Optional[str] = Field(None, description="The ID of the template to render")
    name: Optional[str] = Field(None, description="The name of the template to render")
    context: Optional[dict] = Field(
        None, description="The context variables for rendering the template"
    )
    language: Optional[str] = Field(
        "en", description="The language code of the template"
    )
    category: Optional[TemplateCategory] = Field(
        None, description="The category of the template"
    )

    @model_validator(mode="after")
    def ensure_id_or_name(self):
        if not self.id and not self.name:
            raise ValueError("Either 'id' or 'name' must be provided.")
        return self


class RenderedTemplateData(Schema):
    template_id: str = Field(..., description="The ID of the rendered template")
    template_name: str = Field(..., description="The name of the rendered template")
    version: int = Field(..., description="The version of the rendered template")
    category: TemplateCategory = Field(
        ..., description="The category of the rendered template"
    )
    language: str = Field(..., description="The language of the rendered template")
    subject: Optional[str] = Field(
        None, description="The subject of the rendered template"
    )
    body: str = Field(..., description="The body of the rendered template")


class RenderedTemplateResponse(ApiResponse):
    data: RenderedTemplateData = Field(..., description="The rendered template data")
