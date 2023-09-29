import base64
from io import BytesIO
from datetime import date
from email.mime.image import MIMEImage

from django.test import TestCase, override_settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
try:
    from django.core.files.storage import get_storage_class
except ImportError:
    from django.core.files.storage import storages

    def get_storage_class(s):
        storages[s]

from django.template import TemplateDoesNotExist
from django.core import mail

import pytest
from unittest.mock import patch, Mock
from anymail.message import AnymailMessage

from templated_email.backends.vanilla_django import TemplateBackend, EmailRenderException
from templated_email import InlineImage
from templated_email.models import SavedEmail
from .utils import TempalteBackendBaseMixin
from tests.utils import MockedNetworkTestCaseMixin


PLAIN_RESULT = (u'\n  Hi,\n\n  You just signed up for my website, using:\n    '
                u'  username: vintasoftware\n      join date: Aug. 22, 2016\n'
                u'\n  Thanks, you rock!\n')


HTML_RESULT = (u'<p>Hi Foo Bar,</p><p>You just signed up for my website, '
               u'using:<dl><dt>username</dt><dd>vintasoftwar'
               u'e</dd><dt>join date</dt><dd>Aug. 22, 2016</dd></dl>'
               u'</p><p>Thanks, you rock!</p>')

INHERITANCE_RESULT = (u'<h1>Hello Foo Bar,</h1><p>You just signed up for my website, '
                      u'using:<dl><dt>username</dt><dd>Mr. vintasoftwar'
                      u'e</dd><dt>join date</dt><dd>Aug. 22, 2016</dd></dl>'
                      u'</p>')

GENERATED_PLAIN_RESULT = (u'Hi Foo Bar,\n\nYou just signed up for my website, using:'
                          u'\n\nusername\n\n    vintasoftware\njoin date\n'
                          u'\n    Aug. 22, 2016\n\nThanks, you rock!\n\n')

MULTI_TEMPLATE_PLAIN_RESULT = (u'\nJust to make sure the content is read\n')

SUBJECT_RESULT = 'My subject for vintasoftware'

MULTI_TEMPLATE_SUBJECT_RESULT = 'A subject'

NON_ESCAPED_PLAIN_RESULT = (u'\n  Hi,\n\n  You just signed up for my website, using:\n    '
                            u'  username: <p>vintasoftware</p>\n      join date: Aug. 22, 2016\n'
                            u'\n  Thanks, you rock!\n')


ESCAPED_HTML_RESULT = (u'<p>Hi Foo Bar,</p><p>You just signed up for my website, '
                       u'using:<dl><dt>username</dt><dd>&lt;p&gt;vintasoftwar'
                       u'e&lt;/p&gt;</dd><dt>join date</dt><dd>Aug. 22, 2016</dd></dl>'
                       u'</p><p>Thanks, you rock!</p>')

NON_ESCAPED_SUBJECT_RESULT = 'My subject for <p>vintasoftware</p>'

TXT_FILE = 'test'


def decode_b64_msg(msg):
    return base64.b64decode(msg).decode("utf-8")


class TemplateBackendTestCase(MockedNetworkTestCaseMixin,
                              TempalteBackendBaseMixin, TestCase):
    template_backend_klass = TemplateBackend

    def setUp(self):
        self.backend = self.template_backend_klass()
        self.context = {'username': 'vintasoftware',
                        'joindate': date(2016, 8, 22),
                        'full_name': 'Foo Bar'}

    def test_inexistent_base_email(self):
        try:
            self.backend._render_email('inexistent_base.email', {})
        except TemplateDoesNotExist as e:
            self.assertEqual(e.args[0], 'foo')

    def test_inexistent_template_email(self):
        try:
            self.backend._render_email('foo', {})
        except TemplateDoesNotExist as e:
            self.assertEqual(e.args[0], 'templated_email/foo.email')

    def test_render_plain_email(self):
        response = self.backend._render_email(
            'plain_template.email', self.context)
        self.assertEqual(len(response.keys()), 2)
        self.assertEqual(PLAIN_RESULT, response['plain'])
        self.assertEqual(SUBJECT_RESULT, response['subject'])

    def test_render_html_email(self):
        response = self.backend._render_email(
            'html_template.email', self.context)
        self.assertEqual(len(response.keys()), 2)
        self.assertHTMLEqual(HTML_RESULT, response['html'])
        self.assertEqual(SUBJECT_RESULT, response['subject'])

    def test_render_mixed_email(self):
        response = self.backend._render_email(
            'mixed_template.email', self.context)
        self.assertEqual(len(response.keys()), 3)
        self.assertHTMLEqual(HTML_RESULT, response['html'])
        self.assertEqual(PLAIN_RESULT, response['plain'])
        self.assertEqual(SUBJECT_RESULT, response['subject'])

    def test_render_inheritance_email(self):
        response = self.backend._render_email(
            'inheritance_template.email', self.context)
        self.assertEqual(len(response.keys()), 3)
        self.assertHTMLEqual(INHERITANCE_RESULT, response['html'])
        self.assertEqual(PLAIN_RESULT, response['plain'])
        self.assertEqual('Another subject for vintasoftware', response['subject'])

    def test_email_text_escaping(self):
        self.context['username'] = '<p>vintasoftware</p>'

        response = self.backend._render_email(
            'mixed_template.email', self.context)
        self.assertHTMLEqual(ESCAPED_HTML_RESULT, response['html'])
        self.assertEqual(NON_ESCAPED_PLAIN_RESULT, response['plain'])
        self.assertEqual(NON_ESCAPED_SUBJECT_RESULT, response['subject'])

    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'plain': PLAIN_RESULT, 'subject': SUBJECT_RESULT}
    )
    def test_get_email_message(self, mock):
        message = self.backend.get_email_message(
            'foo.email',
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])
        self.assertTrue(isinstance(message, EmailMessage))
        self.assertEqual(message.body, PLAIN_RESULT)
        self.assertEqual(message.subject, SUBJECT_RESULT)
        self.assertEqual(message.to, ['to@example.com'])
        self.assertEqual(message.cc, ['cc@example.com'])
        self.assertEqual(message.bcc, ['bcc@example.com'])
        self.assertEqual(message.from_email, 'from@example.com')

    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'html': HTML_RESULT, 'plain': PLAIN_RESULT,
                      'subject': SUBJECT_RESULT}
    )
    def test_get_email_message_with_create_link(self, mocked):
        self.backend.get_email_message(
            'foo.email',
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'],
            create_link=True)
        first_call_context = mocked.call_args_list[0][0][1]
        uuid = first_call_context['email_uuid']
        self.assertTrue(uuid)
        second_call_context = mocked.call_args_list[1][0][1]
        self.assertEqual(len(second_call_context), 0)
        saved_email = SavedEmail.objects.get(
            uuid=uuid)
        self.assertEqual(saved_email.content, HTML_RESULT)

    @patch('django.core.files.storage.FileSystemStorage.save')
    @patch('django.core.files.storage.FileSystemStorage.url')
    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'html': HTML_RESULT, 'plain': PLAIN_RESULT,
                      'subject': SUBJECT_RESULT}
    )
    def test_get_email_message_with_inline_image(self, mock_render_email, mock_url, mock_save):
        mock_url.return_value = 'media/saved_url'
        self.backend.get_email_message(
            'foo.email', {'an_image': InlineImage('file.png', b'foo',
                                                    subtype='png')},
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'],
            create_link=True)
        second_call_context = mock_render_email.call_args_list[1][0][1]
        self.assertEqual(second_call_context['an_image'], 'media/saved_url')

    @override_settings(TEMPLATED_EMAIL_EMAIL_MESSAGE_CLASS='anymail.message.AnymailMessage')
    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'plain': PLAIN_RESULT, 'subject': SUBJECT_RESULT}
    )
    def test_custom_emailmessage_klass(self, mock):
        message = self.backend.get_email_message(
            'foo.email',
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])
        self.assertTrue(isinstance(message, AnymailMessage))

    @override_settings(TEMPLATED_EMAIL_DJANGO_SUBJECTS={'foo.email':
                                                        'foo\r\n'})
    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'plain': PLAIN_RESULT}
    )
    def test_get_email_message_without_subject(self, mock):
        message = self.backend.get_email_message(
            'foo.email',
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])
        self.assertTrue(isinstance(message, EmailMessage))
        self.assertEqual(message.body, PLAIN_RESULT)
        self.assertEqual(message.subject, 'foo')
        self.assertEqual(message.to, ['to@example.com'])
        self.assertEqual(message.cc, ['cc@example.com'])
        self.assertEqual(message.bcc, ['bcc@example.com'])
        self.assertEqual(message.from_email, 'from@example.com')

    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'plain': PLAIN_RESULT, 'subject': SUBJECT_RESULT}
    )
    def test_get_email_message_without_from_email_when_no_default_email_is_set(self, mock):
        message = self.backend.get_email_message(
            'foo.email', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])
        self.assertTrue(isinstance(message, EmailMessage))
        self.assertEqual(message.body, PLAIN_RESULT)
        self.assertEqual(message.subject, SUBJECT_RESULT)
        self.assertEqual(message.to, ['to@example.com'])
        self.assertEqual(message.cc, ['cc@example.com'])
        self.assertEqual(message.bcc, ['bcc@example.com'])
        self.assertEqual(message.from_email, 'webmaster@localhost')

    @override_settings(TEMPLATED_EMAIL_FROM_EMAIL='default.templated.email@localhost')
    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'plain': PLAIN_RESULT, 'subject': SUBJECT_RESULT}
    )
    def test_get_email_message_without_from_email_when_templated_email_from_email_is_set(self, mock):
        message = self.backend.get_email_message(
            'foo.email', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])
        self.assertTrue(isinstance(message, EmailMessage))
        self.assertEqual(message.body, PLAIN_RESULT)
        self.assertEqual(message.subject, SUBJECT_RESULT)
        self.assertEqual(message.to, ['to@example.com'])
        self.assertEqual(message.cc, ['cc@example.com'])
        self.assertEqual(message.bcc, ['bcc@example.com'])
        self.assertEqual(message.from_email, 'default.templated.email@localhost')

    @override_settings(TEMPLATED_EMAIL_FROM_EMAIL='default.templated.email@localhost', DEFAULT_FROM_EMAIL='default.email@localhost')
    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'plain': PLAIN_RESULT, 'subject': SUBJECT_RESULT}
    )
    def test_get_email_message_without_from_email_when_default_email_is_set(self, mock):
        message = self.backend.get_email_message(
            'foo.email', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])
        self.assertTrue(isinstance(message, EmailMessage))
        self.assertEqual(message.body, PLAIN_RESULT)
        self.assertEqual(message.subject, SUBJECT_RESULT)
        self.assertEqual(message.to, ['to@example.com'])
        self.assertEqual(message.cc, ['cc@example.com'])
        self.assertEqual(message.bcc, ['bcc@example.com'])
        self.assertEqual(message.from_email, 'default.templated.email@localhost')

    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'plain': PLAIN_RESULT, 'subject': SUBJECT_RESULT}
    )
    def test_get_email_message_without_recipient_list(self, mock):
        message = self.backend.get_email_message(
            'foo.email',
            from_email='from@example.com')
        self.assertTrue(isinstance(message, EmailMessage))
        self.assertEqual(message.body, PLAIN_RESULT)
        self.assertEqual(message.subject, SUBJECT_RESULT)
        self.assertEqual(message.to, [])
        self.assertEqual(message.cc, [])
        self.assertEqual(message.bcc, [])
        self.assertEqual(message.from_email, 'from@example.com')

    @override_settings(TEMPLATED_EMAIL_DJANGO_SUBJECTS={'foo.email':
                                                        'foo\r\n'})
    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'plain': PLAIN_RESULT}
    )
    def test_get_email_message_without_subject_multiple_templates(self, mock):
        message = self.backend.get_email_message(
            ['woo.email', 'foo.email'],
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])
        self.assertTrue(isinstance(message, EmailMessage))
        self.assertEqual(message.body, PLAIN_RESULT)
        self.assertEqual(message.subject, 'foo')
        self.assertEqual(message.to, ['to@example.com'])
        self.assertEqual(message.cc, ['cc@example.com'])
        self.assertEqual(message.bcc, ['bcc@example.com'])
        self.assertEqual(message.from_email, 'from@example.com')

    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'html': HTML_RESULT, 'subject': SUBJECT_RESULT}
    )
    def test_get_email_message_generated_plain_text(self, mock):
        message = self.backend.get_email_message(
            'foo.email',
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])
        self.assertTrue(isinstance(message, EmailMultiAlternatives))
        self.assertHTMLEqual(message.alternatives[0][0], HTML_RESULT)
        self.assertEqual(message.alternatives[0][1], 'text/html')
        self.assertEqual(message.body, GENERATED_PLAIN_RESULT)
        self.assertEqual(message.subject, SUBJECT_RESULT)
        self.assertEqual(message.to, ['to@example.com'])
        self.assertEqual(message.cc, ['cc@example.com'])
        self.assertEqual(message.bcc, ['bcc@example.com'])
        self.assertEqual(message.from_email, 'from@example.com')

    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'html': HTML_RESULT, 'subject': SUBJECT_RESULT}
    )
    @override_settings(TEMPLATED_EMAIL_PLAIN_FUNCTION=lambda x: 'hi')
    def test_get_email_message_custom_func_generated_plain_text(self, mock):
        message = self.backend.get_email_message('foo.email')
        self.assertEqual(message.body, 'hi')

    def test_get_multi_match_last_email_message_generated_plain_text(self):
        message = self.backend.get_email_message(
            ['multi-template.email', 'foo.email', ],
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])
        self.assertEqual(message.body, MULTI_TEMPLATE_PLAIN_RESULT)
        self.assertEqual(message.subject, MULTI_TEMPLATE_SUBJECT_RESULT)
        self.assertEqual(message.to, ['to@example.com'])
        self.assertEqual(message.cc, ['cc@example.com'])
        self.assertEqual(message.bcc, ['bcc@example.com'])
        self.assertEqual(message.from_email, 'from@example.com')

    def test_get_multi_first_match_email_message_generated_plain_text(self):
        message = self.backend.get_email_message(
            ['foo.email', 'multi-template.email', ],
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])
        self.assertEqual(message.body, MULTI_TEMPLATE_PLAIN_RESULT)
        self.assertEqual(message.subject, MULTI_TEMPLATE_SUBJECT_RESULT)
        self.assertEqual(message.to, ['to@example.com'])
        self.assertEqual(message.cc, ['cc@example.com'])
        self.assertEqual(message.bcc, ['bcc@example.com'])
        self.assertEqual(message.from_email, 'from@example.com')

    def test_get_multi_options_select_last_plain_only(self):
        message = self.backend.get_email_message(
            ['non-existing.email', 'also-non-existing.email', 'non-existing-without-suffix', 'foo.email', 'multi-template.email', ],
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])
        self.assertEqual(message.body, MULTI_TEMPLATE_PLAIN_RESULT)
        self.assertEqual(message.subject, MULTI_TEMPLATE_SUBJECT_RESULT)
        self.assertEqual(message.to, ['to@example.com'])
        self.assertEqual(message.cc, ['cc@example.com'])
        self.assertEqual(message.bcc, ['bcc@example.com'])
        self.assertEqual(message.from_email, 'from@example.com')

    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'html': HTML_RESULT, 'plain': PLAIN_RESULT,
                      'subject': SUBJECT_RESULT}
    )
    def test_get_email_message_with_plain_and_html(self, mock):
        message = self.backend.get_email_message(
            'foo.email',
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])
        self.assertTrue(isinstance(message, EmailMultiAlternatives))
        self.assertHTMLEqual(message.alternatives[0][0], HTML_RESULT)
        self.assertEqual(message.alternatives[0][1], 'text/html')
        self.assertEqual(message.body, PLAIN_RESULT)
        self.assertEqual(message.subject, SUBJECT_RESULT)
        self.assertEqual(message.to, ['to@example.com'])
        self.assertEqual(message.cc, ['cc@example.com'])
        self.assertEqual(message.bcc, ['bcc@example.com'])
        self.assertEqual(message.from_email, 'from@example.com')

    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'subject': SUBJECT_RESULT}
    )
    def test_get_email_message_with_no_body_parts(self, mock):
        with pytest.raises(EmailRenderException):
            self.backend.get_email_message(
                'foo.email',
                from_email='from@example.com', cc=['cc@example.com'],
                bcc=['bcc@example.com'], to=['to@example.com'])

    @override_settings(TEMPLATED_EMAIL_EMAIL_MULTIALTERNATIVES_CLASS='anymail.message.AnymailMessage')
    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'html': HTML_RESULT, 'plain': PLAIN_RESULT,
                      'subject': SUBJECT_RESULT}
    )
    def test_custom_emailmessage_klass_multipart(self, mock):
        message = self.backend.get_email_message(
            'foo.email',
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])
        self.assertTrue(isinstance(message, AnymailMessage))

    @override_settings(TEMPLATED_EMAIL_AUTO_PLAIN=False)
    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'html': HTML_RESULT,
                      'subject': SUBJECT_RESULT}
    )
    def test_get_email_message_html_only(self, mock):
        message = self.backend.get_email_message(
            'foo.email',
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'])
        self.assertTrue(isinstance(message, EmailMessage))
        self.assertHTMLEqual(message.body, HTML_RESULT)
        self.assertEqual(message.content_subtype, 'html')
        self.assertEqual(message.subject, SUBJECT_RESULT)
        self.assertEqual(message.to, ['to@example.com'])
        self.assertEqual(message.cc, ['cc@example.com'])
        self.assertEqual(message.bcc, ['bcc@example.com'])
        self.assertEqual(message.from_email, 'from@example.com')

    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'html': HTML_RESULT, 'plain': PLAIN_RESULT,
                      'subject': SUBJECT_RESULT}
    )
    def test_send(self, render_mock):
        ret = self.backend.send('mixed_template', 'from@example.com',
                                ['to@example.com', 'to2@example.com'],
                                headers={'Message-Id': 'a_message_id'})
        self.assertEqual(ret, 'a_message_id')
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(ret, message.extra_headers['Message-Id'])
        self.assertTrue(isinstance(message, EmailMultiAlternatives))
        self.assertHTMLEqual(message.alternatives[0][0], HTML_RESULT)
        self.assertEqual(message.alternatives[0][1], 'text/html')
        self.assertEqual(message.body, PLAIN_RESULT)
        self.assertEqual(message.subject, SUBJECT_RESULT)
        self.assertEqual(message.to, ['to@example.com', 'to2@example.com'])
        self.assertEqual(message.from_email, 'from@example.com')

    @patch.object(
        template_backend_klass, 'get_email_message'
    )
    @patch(
        'templated_email.backends.vanilla_django.get_connection'
    )
    def test_all_arguments_passed_forward_from_send(
            self, get_connection_mock, get_email_message_mock):
        kwargs = {
            'template_name': 'foo',
            'from_email': 'from@example.com',
            'recipient_list': ['to@example.com'],
            'context': {'foo': 'bar'},
            'cc': ['cc@example.com'],
            'bcc': ['bcc@example.com'],
            'fail_silently': True,
            'headers': {'Message-Id': 'a_message_id'},
            'template_prefix': 'prefix',
            'template_suffix': 'suffix',
            'template_dir': 'tempdir',
            'file_extension': 'ext',
            'auth_user': 'vintasoftware',
            'auth_password': 'password',
            'create_link': False,
        }

        send_mock = get_email_message_mock.return_value.send
        self.backend.send(**kwargs)
        get_connection_mock.assert_called_with(
            username=kwargs['auth_user'],
            password=kwargs['auth_password'],
            fail_silently=kwargs['fail_silently']
        )
        get_email_message_mock.assert_called_with(
            kwargs['template_name'],
            kwargs['context'],
            from_email=kwargs['from_email'],
            to=kwargs['recipient_list'],
            cc=kwargs['cc'],
            bcc=kwargs['bcc'],
            headers=kwargs['headers'],
            template_prefix=kwargs['template_prefix'],
            template_suffix=kwargs['template_suffix'],
            template_dir=kwargs['template_dir'],
            file_extension=kwargs['file_extension'],
            create_link=kwargs['create_link'],
            attachments=None,
        )
        send_mock.assert_called_with(
            kwargs['fail_silently']
        )

    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'plain': PLAIN_RESULT,
                      'subject': SUBJECT_RESULT}
    )
    def test_send_attachment_mime_base(self, render_mock):
        self.backend.send('plain_template', 'from@example.com',
                          ['to@example.com', 'to2@example.com'],
                          attachments=[MIMEImage(TXT_FILE, 'text/plain')])
        attachment = mail.outbox[0].attachments[0]
        self.assertEqual(decode_b64_msg(attachment.get_payload()),
                         TXT_FILE)

    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'plain': PLAIN_RESULT,
                      'subject': SUBJECT_RESULT}
    )
    def test_send_attachment_tripple(self, render_mock):
        self.backend.send('plain_template', 'from@example.com',
                          ['to@example.com', 'to2@example.com'],
                          attachments=[('black_pixel.png', TXT_FILE, 'text/plain')])
        attachment = mail.outbox[0].attachments[0]
        self.assertEqual(('black_pixel.png', TXT_FILE, 'text/plain'),
                         attachment)

    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'plain': PLAIN_RESULT, 'subject': SUBJECT_RESULT}
    )
    def test_get_email_message_attachment_mime_base(self, mock):
        message = self.backend.get_email_message(
            'foo.email',
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'],
            attachments=[MIMEImage(TXT_FILE, 'text/plain')])
        attachment = message.attachments[0]
        self.assertEqual(decode_b64_msg(attachment.get_payload()),
                         TXT_FILE)

    @patch.object(
        template_backend_klass, '_render_email',
        return_value={'plain': PLAIN_RESULT, 'subject': SUBJECT_RESULT}
    )
    def test_get_email_message_attachment_tripple(self, mock):
        message = self.backend.get_email_message(
            'foo.email',
            from_email='from@example.com', cc=['cc@example.com'],
            bcc=['bcc@example.com'], to=['to@example.com'],
            attachments=[('black_pixel.png', TXT_FILE, 'text/plain')])
        attachment = message.attachments[0]
        self.assertEqual(('black_pixel.png', TXT_FILE, 'text/plain'),
                         attachment)

    def test_removal_of_legacy(self):
        try:
            self.backend._render_email('legacy', {})
        except TemplateDoesNotExist as e:
            self.assertEqual(e.args[0], 'templated_email/legacy.email')

    @patch('django.core.files.storage.FileSystemStorage.url')
    @patch('django.core.files.storage.FileSystemStorage.save')
    def test_host_inline_image_if_not_exist(self, mock_save, mock_url):
        mock_url.return_value = 'media/saved_url'
        inline_image = InlineImage('foo.jpg', b'bar')

        filename = self.backend.host_inline_image(inline_image)
        self.assertEqual(filename, 'media/saved_url')
        mock_save.assert_called_once()
        name, content = mock_save.call_args[0]
        self.assertEqual(
            name,
            'templated_email/37b51d194a7513e45b56f6524f2d51f2foo.jpg')
        self.assertTrue(isinstance(content, BytesIO))

    @patch('django.core.files.storage.FileSystemStorage.exists')
    @patch('django.core.files.storage.FileSystemStorage.save')
    def test_host_inline_image_if_exist(self, mock_save, mock_exists):
        inline_image = InlineImage('foo.jpg', b'bar')
        mock_exists.return_value = True

        filename = self.backend.host_inline_image(inline_image)
        self.assertEqual(
            filename,
            '/media/templated_email/37b51d194a7513e45b56f6524f2d51f2foo.jpg')

        mock_save.assert_not_called()
        mock_exists.assert_called_once_with(
            'templated_email/37b51d194a7513e45b56f6524f2d51f2foo.jpg')
