import mock
from email.utils import unquote

from django.test import TestCase

from templated_email.backends.vanilla_django import TemplateBackend
from templated_email import InlineImage


class InlineMessageTestCase(TestCase):
    def setUp(self):
        self.inline_image = InlineImage('foo.png', 'content', 'png')

    def test_needs_two_args(self):
        with self.assertRaises(TypeError):
            InlineImage()
        with self.assertRaises(TypeError):
            InlineImage('foo')

    def test_has_no_cid(self):
        self.assertIsNone(self.inline_image._content_id)

    def test_generate_cid(self):
        str(self.inline_image)
        self.assertIsNotNone(self.inline_image._content_id)

    @mock.patch('templated_email.utils.make_msgid', return_value='foo')
    def test_str(self, mocked):
        self.assertEqual(str(self.inline_image), 'cid:foo')

    def test_attach_to_message(self):
        message = mock.Mock()
        self.inline_image.attach_to_message(message)
        mimeimage = message.attach.call_args[0][0]
        self.assertEquals(mimeimage.get('Content-ID'),
                          self.inline_image._content_id)
        self.assertEquals(mimeimage.get('Content-Disposition'),
                          'inline; filename="foo.png"')
