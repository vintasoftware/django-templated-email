from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from templated_email import get_connection, backends


class GetConnectionTestCase(TestCase):
    def test_default(self):
        connection = get_connection()

        self.assertIsInstance(connection,
                              backends.vanilla_django.TemplateBackend)

    def test_class_name(self):
        klass = 'templated_email.backends.vanilla_django.TemplateBackend'

        connection = get_connection(klass)

        self.assertIsInstance(connection,
                              backends.vanilla_django.TemplateBackend)

    def test_class_instance(self):
        klass = backends.vanilla_django.TemplateBackend

        connection = get_connection(klass)

        self.assertIsInstance(connection, klass)

    def test_non_existing_module(self):
        klass = 'templated_email.backends.non_existing.NoBackend'

        self.assertRaises(ImproperlyConfigured, get_connection, klass)

    def test_non_existing_class(self):
        klass = 'templated_email.backends.vanilla_django.NoBackend'

        self.assertRaises(ImproperlyConfigured, get_connection, klass)
