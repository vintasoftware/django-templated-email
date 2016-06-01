from django.core.mail import EmailMessage
from django.test import TestCase

from templated_email.backends.vanilla_django import TemplateBackend


class VanillaDjangoTests(TestCase):
    backend = TemplateBackend()

    def test_email(self):
        email = self.backend.get_email_message('test', {})

        self.assertIsInstance(email, EmailMessage)
        self.assertEqual(email.subject, u'The Subject!')
        self.assertEqual(email.body, u'\nThe plaintext body.\n')
