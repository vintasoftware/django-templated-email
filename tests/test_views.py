import uuid

from django.urls import reverse
from django.test import TestCase
from django.test import Client

from templated_email.models import SavedEmail


class ShowEmailViewTestCase(TestCase):

    def setUp(self):
        self.uuid = uuid.uuid4()
        self.saved_email = SavedEmail.objects.create(uuid=self.uuid, content='foo')
        self.url = '/email/%s/' % self.uuid
        self.url_hex = '/email/%s/' % self.uuid.hex
        self.client = Client()

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_hex(self):
        response = self.client.get(self.url_hex)
        self.assertEqual(response.status_code, 200)

    def test_get_non_valid(self):
        response = self.client.get('/email/bar/')
        self.assertEqual(response.status_code, 404)

    def test_url(self):
        self.assertEqual(
            reverse('templated_email:show_email',
                    kwargs={'uuid': self.saved_email.uuid}),
            self.url)

    def test_url_hex(self):
        self.assertEqual(
            reverse('templated_email:show_email',
                    kwargs={'uuid': self.saved_email.uuid.hex}),
            self.url_hex)
