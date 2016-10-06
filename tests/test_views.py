import uuid

from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse

from templated_email.models import SavedEmail


class ShowEmailViewTestCase(TestCase):

    def setUp(self):
        self.uuid = uuid.uuid4()
        self.saved_email = SavedEmail.objects.create(uuid=self.uuid, content='foo')
        self.url = '/email/%s/' % self.uuid
        self.client = Client()

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url(self):
        self.assertEquals(
            reverse('templated_email:show_email',
                    kwargs={'uuid': self.saved_email.uuid}),
            self.url)
