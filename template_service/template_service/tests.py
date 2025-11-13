import json
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.core.cache import cache
from django.urls import reverse
from ninja.testing import TestClient

from template_service.models import Template, TemplateCategory
from template_service.api import router
from template_service.services import TemplateService


class TemplateServiceTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = TestClient(router)
        cache.clear()

        # Create test template
        self.template_data = {
            "name": "welcome_email",
            "category": "email",
            "subject": "Welcome {{user_name}}!",
            "body": "Hello {{user_name}}, welcome to our platform!",
            "language": "en",
            "context": ["user_name"],
        }

        self.template = Template.objects.create(**self.template_data)

    def tearDown(self):
        """Clean up after each test"""
        cache.clear()


class TemplateAPITestCase(TemplateServiceTestCase):
    """Test cases for Template API endpoints"""

    def test_create_template_success(self):
        """Test successful template creation"""
        new_template_data = {
            "name": "password_reset",
            "category": "email",
            "subject": "Reset Your Password",
            "body": "Click here to reset: {{reset_link}}",
            "language": "en",
            "context": ["reset_link"],
        }

        response = self.client.post("/templates", json=new_template_data)

        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["message"], "Template created successfully")
        self.assertEqual(response_data["data"]["name"], "password_reset")
        self.assertEqual(response_data["data"]["version"], 1)

    def test_create_template_versioning(self):
        """Test that creating template with same name increments version"""
        new_template_data = {
            "name": "welcome_email",  # Same name as existing template
            "category": "email",
            "subject": "Updated Welcome {{user_name}}!",
            "body": "Updated body for {{user_name}}",
            "language": "en",
            "context": ["user_name"],
        }

        response = self.client.post("/templates", json=new_template_data)

        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(response_data["data"]["version"], 2)  # Should be version 2

    def test_create_template_validation_error(self):
        """Test template creation with invalid data"""
        invalid_data = {
            "name": "",  # Empty name should fail validation
            "category": "email",
            "body": "Test body",
        }

        response = self.client.post("/templates", json=invalid_data)

        self.assertEqual(
            response.status_code, 422
        )  # Django Ninja returns 422 for validation errors

    def test_update_template_success(self):
        """Test successful template update"""
        update_data = {
            "subject": "Updated Subject {{user_name}}",
            "body": "Updated body content for {{user_name}}",
        }

        response = self.client.patch(f"/templates/{self.template.id}", json=update_data)

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["message"], "Template updated successfully")
        self.assertEqual(
            response_data["data"]["subject"], "Updated Subject {{user_name}}"
        )
        self.assertEqual(response_data["data"]["version"], 2)  # New version created

    def test_update_template_not_found(self):
        """Test updating non-existent template"""
        fake_id = "550e8400-e29b-41d4-a716-446655440999"
        update_data = {"subject": "Updated Subject"}

        response = self.client.patch(f"/templates/{fake_id}", json=update_data)

        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertFalse(response_data["success"])

    def test_get_all_templates_success(self):
        """Test getting all templates"""
        response = self.client.get("/templates")

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("data", response_data)
        self.assertIn("meta", response_data)
        self.assertTrue(len(response_data["data"]) >= 1)

    def test_get_all_templates_with_filters(self):
        """Test getting templates with filters"""
        # Create another template with different category
        Template.objects.create(
            name="push_notification",
            category="push",
            body="Push notification body",
            language="en",
        )

        # Filter by email category
        response = self.client.get("/templates?category=email")

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        for template in response_data["data"]:
            self.assertEqual(template["category"], "email")

    def test_get_all_templates_pagination(self):
        """Test pagination functionality"""
        # Create multiple templates
        for i in range(25):
            Template.objects.create(
                name=f"template_{i}", category="email", body=f"Body {i}", language="en"
            )

        # Test first page
        response = self.client.get("/templates?page=1&limit=10")

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data["data"]), 10)
        self.assertEqual(response_data["meta"]["page"], 1)
        self.assertEqual(response_data["meta"]["limit"], 10)
        self.assertTrue(response_data["meta"]["has_next"])

    def test_get_template_by_id_success(self):
        """Test getting template by ID"""
        response = self.client.get(f"/templates/{self.template.id}")

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["data"]["id"], str(self.template.id))
        self.assertEqual(response_data["data"]["name"], "welcome_email")

    def test_get_template_by_id_not_found(self):
        """Test getting non-existent template by ID"""
        fake_id = "550e8400-e29b-41d4-a716-446655440999"
        response = self.client.get(f"/templates/{fake_id}")

        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertFalse(response_data["success"])

    def test_render_template_by_id_success(self):
        """Test rendering template by ID"""
        render_data = {
            "id": str(self.template.id),
            "context": {"user_name": "John Doe"},
        }

        response = self.client.post("/render", json=render_data)

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["data"]["template_id"], str(self.template.id))
        self.assertIn("John Doe", response_data["data"]["subject"])
        self.assertIn("John Doe", response_data["data"]["body"])

    def test_render_template_by_name_success(self):
        """Test rendering template by name"""
        render_data = {
            "name": "welcome_email",
            "category": "email",
            "language": "en",
            "context": {"user_name": "Jane Smith"},
        }

        response = self.client.post("/render", json=render_data)

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["data"]["template_name"], "welcome_email")
        self.assertIn("Jane Smith", response_data["data"]["subject"])

    def test_render_template_missing_context(self):
        """Test rendering template with missing context variables"""
        render_data = {
            "id": str(self.template.id),
            "context": {},  # Missing user_name
        }

        response = self.client.post("/render", json=render_data)

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn("Template rendering failed", response_data["message"])

    def test_render_template_no_id_or_name(self):
        """Test rendering template without providing ID or name"""
        render_data = {"context": {"user_name": "John Doe"}}

        response = self.client.post("/render", json=render_data)

        self.assertEqual(response.status_code, 422)  # Validation error

    def test_delete_template_success(self):
        """Test successful template deletion"""
        response = self.client.delete(f"/templates/{self.template.id}")

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data["success"])

        # Verify template is soft deleted
        self.template.refresh_from_db()
        self.assertTrue(self.template.is_deleted)

    def test_delete_template_not_found(self):
        """Test deleting non-existent template"""
        fake_id = "550e8400-e29b-41d4-a716-446655440999"
        response = self.client.delete(f"/templates/{fake_id}")

        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertFalse(response_data["success"])


class TemplateServiceBusinessLogicTestCase(TemplateServiceTestCase):
    """Test cases for TemplateService business logic"""

    def test_create_template_service(self):
        """Test TemplateService.create_template method"""
        from template_service.schemas import CreateTemplate

        new_data = CreateTemplate(
            name="service_test",
            category="email",
            subject="Test Subject",
            body="Test Body",
            language="en",
        )

        template = TemplateService.create_template(new_data)

        self.assertIsInstance(template, Template)
        self.assertEqual(template.name, "service_test")
        self.assertEqual(template.version, 1)

    def test_update_template_service(self):
        """Test TemplateService.update_template method"""
        from template_service.schemas import UpdateTemplate

        update_data = UpdateTemplate(
            subject="Updated Service Subject", body="Updated Service Body"
        )

        updated_template = TemplateService.update_template(
            str(self.template.id), update_data
        )

        self.assertIsInstance(updated_template, Template)
        self.assertEqual(updated_template.subject, "Updated Service Subject")
        self.assertEqual(updated_template.version, 2)

    def test_get_latest_template(self):
        """Test TemplateService.get_latest_template method"""
        latest = TemplateService.get_latest_template(
            name="welcome_email", category="email", language="en"
        )

        self.assertEqual(latest.id, self.template.id)

    def test_render_template_service(self):
        """Test TemplateService.render_template method"""
        render_request = MagicMock()
        render_request.id = str(self.template.id)
        render_request.name = None
        render_request.context = {"user_name": "Test User"}

        result = TemplateService.render_template(render_request)

        self.assertEqual(result["template_id"], str(self.template.id))
        self.assertIn("Test User", result["subject"])

    def test_replace_variables(self):
        """Test variable replacement functionality"""
        text = "Hello {{name}}, your order {{order_id}} is ready!"
        context = {"name": "John", "order_id": "12345"}

        result = TemplateService._replace_variables(text, context)

        self.assertEqual(result, "Hello John, your order 12345 is ready!")

    def test_replace_variables_missing_context(self):
        """Test variable replacement with missing context"""
        text = "Hello {{name}}, your order {{order_id}} is ready!"
        context = {"name": "John"}  # Missing order_id

        result = TemplateService._replace_variables(text, context)

        self.assertEqual(result, "Hello John, your order {{order_id}} is ready!")


class TemplateCacheTestCase(TemplateServiceTestCase):
    """Test cases for caching functionality"""

    @patch("template_service.services.cache")
    def test_cache_hit_for_template_by_id(self, mock_cache):
        """Test cache hit when getting template by ID"""
        # Mock cache hit
        mock_cache.get.return_value = self.template

        result = TemplateService.get_template_by_id(str(self.template.id))

        self.assertEqual(result, self.template)
        mock_cache.get.assert_called_once()

    @patch("template_service.services.cache")
    def test_cache_miss_for_template_by_id(self, mock_cache):
        """Test cache miss when getting template by ID"""
        # Mock cache miss
        mock_cache.get.return_value = None

        result = TemplateService.get_template_by_id(str(self.template.id))

        self.assertEqual(result, self.template)
        mock_cache.set.assert_called_once()

    @patch("template_service.services.cache")
    def test_cache_invalidation_on_create(self, mock_cache):
        """Test cache invalidation on template creation"""
        from template_service.schemas import CreateTemplate

        new_data = CreateTemplate(
            name="cache_test", category="email", body="Test body", language="en"
        )

        TemplateService.create_template(new_data)

        # Verify cache delete was called
        mock_cache.delete_many.assert_called()

    @patch("template_service.services.cache")
    def test_cache_invalidation_on_update(self, mock_cache):
        """Test cache invalidation on template update"""
        from template_service.schemas import UpdateTemplate

        update_data = UpdateTemplate(subject="Updated Subject")

        TemplateService.update_template(str(self.template.id), update_data)

        # Verify cache delete was called
        mock_cache.delete_many.assert_called()

    def test_cache_keys_generation(self):
        """Test cache key generation methods"""
        from template_service.services import TemplateCacheKeys

        # Test template_by_id key
        key = TemplateCacheKeys.template_by_id("test-id")
        self.assertEqual(key, "template:id:test-id")

        # Test template_latest key
        key = TemplateCacheKeys.template_latest("test", "email", "en")
        self.assertEqual(key, "template:latest:test:email:en")

        # Test template_versions key
        key = TemplateCacheKeys.template_versions("test", "email", "en")
        self.assertEqual(key, "template:versions:test:email:en")


class TemplateModelTestCase(TemplateServiceTestCase):
    """Test cases for Template model"""

    def test_template_string_representation(self):
        """Test Template model __str__ method"""
        expected = f"{self.template.name} ({self.template.category}) - [lang: {self.template.language}] - v{self.template.version}"
        self.assertEqual(str(self.template), expected)

    def test_template_get_latest_version(self):
        """Test Template model get_latest_version method"""
        latest = self.template.get_latest_version()
        self.assertEqual(latest.id, self.template.id)

    def test_template_unique_constraint(self):
        """Test unique constraint on name, category, language, version"""
        # This should raise an IntegrityError due to unique constraint
        with self.assertRaises(Exception):  # Will be IntegrityError in real database
            Template.objects.create(
                name=self.template.name,
                category=self.template.category,
                language=self.template.language,
                version=self.template.version,  # Same version
                body="Different body",
            )

    def test_template_soft_delete(self):
        """Test soft delete functionality"""
        template_id = self.template.id

        # Soft delete
        TemplateService.delete_template(str(template_id))

        # Verify it's soft deleted
        self.template.refresh_from_db()
        self.assertTrue(self.template.is_deleted)

        # Verify it's not returned in normal queries
        self.assertFalse(
            Template.objects.filter(id=template_id, is_deleted=False).exists()
        )
