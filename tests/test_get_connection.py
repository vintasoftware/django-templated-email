from django.test import TestCase

from templated_email import get_default_template_backend, backends


class GetConnectionTestCase(TestCase):
    def test_default(self):
        connection = get_default_template_backend()

        self.assertIsInstance(connection,
                              backends.vanilla_django.TemplateBackend)

    def test_class_name(self):
        klass = 'templated_email.backends.vanilla_django.TemplateBackend'

        connection = get_default_template_backend(klass)

        self.assertIsInstance(connection,
                              backends.vanilla_django.TemplateBackend)

    def test_class_name_omitted(self):
        klass = 'templated_email.backends.vanilla_django'

        connection = get_default_template_backend(klass)

        self.assertIsInstance(connection,
                              backends.vanilla_django.TemplateBackend)

    def test_class_instance(self):
        klass = backends.vanilla_django.TemplateBackend

        connection = get_default_template_backend(klass)

        self.assertIsInstance(connection, klass)

    def test_non_existing_module(self):
        klass = 'templated_email.backends.non_existing.NoBackend'

        self.assertRaises(ImportError, get_default_template_backend, klass)

    def test_non_existing_class(self):
        klass = 'templated_email.backends.vanilla_django.NoBackend'

        self.assertRaises(ImportError, get_default_template_backend, klass)
