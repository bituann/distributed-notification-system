from django.contrib import admin

from template_service.models import Template

admin.site.site_header = "Template Service Admin"
admin.site.register(Template)
