from uuid import uuid4

from django.db import models


class TemplateCategory(models.TextChoices):
    email = "email", "Email"
    push = "push", "Push Notification"


class Template(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=20,
        choices=TemplateCategory.choices,
        default=TemplateCategory.email,
    )
    subject = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField()
    language = models.CharField(max_length=10, default="en", db_index=True)
    version = models.IntegerField(default=1)

    context = models.JSONField(default=list, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "templates"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name", "category", "language", "-version"]),
            models.Index(fields=["is_active", "is_deleted"]),
        ]
        # makes sure these fields are unique together or no??
        unique_together = [["name", "category", "language", "version"]]

    def __str__(self):
        return (
            f"{self.name} ({self.category}) - [lang: {self.language}] - v{self.version}"
        )

    def get_latest_version(self):
        template = (
            Template.objects.filter(
                name=self.name,
                category=self.category,
                language=self.language,
                is_deleted=False,
            )
            .order_by("-version")
            .first()
        )
        return template if template else None
