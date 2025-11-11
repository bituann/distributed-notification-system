from enum import Enum
from typing import Generic, List, Optional, TypeVar

from ninja import Field, ModelSchema, Schema

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
