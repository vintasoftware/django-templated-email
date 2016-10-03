import base64
from email.utils import unquote

from django.test import TestCase

from templated_email.backends.vanilla_django import TemplateBackend
from templated_email import InlineImage

from tests.utils import MockedNetworkTestCaseMixin

imageb64 = ('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1B'
            'MVEUAAACnej3aAAAAAXRSTlMAQObYZgAAAApJREFUCNdjYAAAAAIAAeIhvD'
            'MAAAAASUVORK5CYII=')


class GetMessageWithInlineMessageTestCase(MockedNetworkTestCaseMixin, TestCase):
    def setUp(self):
        self.backend = TemplateBackend()
        self.inline_image = InlineImage('foo.png', base64.b64decode(imageb64))
        self.message = self.backend.get_email_message(
            'inline_image.email', {'image_file': self.inline_image},
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])

    def test_cid_in_message(self):
        alternative_message = self.message.alternatives[0][0]
        self.assertIn('cid:%s' % unquote(self.inline_image._content_id),
                      alternative_message)

    def test_image_in_attachments(self):
        mimage = self.message.attachments[0]
        attachment_content = base64.b64encode(mimage.get_payload(decode=True))
        self.assertEquals(attachment_content.decode(), imageb64)
