import os, unittest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

from django.test.utils import setup_test_environment
setup_test_environment()

from templated_email import get_connection
from templated_email.backends.vanilla_django import TemplateBackend



class TestGetConnection(unittest.TestCase):

    def test_can_accept_path_to_class_as_backend(self):
	self.assertIsInstance(get_connection('templated_email.backends.vanilla_django.TemplateBackend'), TemplateBackend)

    def test_can_accept_path_to_module_as_backend(self):
	self.assertIsInstance(get_connection('templated_email.backends.vanilla_django'), TemplateBackend)




if __name__ == '__main__':
    unittest.main()
