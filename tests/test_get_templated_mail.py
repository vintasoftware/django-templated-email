from django.test import TestCase

from mock import patch

from templated_email import get_templated_mail


class GetTemplatedMailTestCase(TestCase):
    TEST_ARGS = ['a_template_name', {'context': 'content'}]
    TEST_KWARGS = {
        'from_email': 'from@example.com',
        'to': ['to@example.com'],
        'cc': ['cc@example.com'],
        'bcc': ['bcc@example.com'],
        'headers': {'A_HEADER': 'foo'},
        'template_prefix': 'prefix',
        'template_suffix': 'suffix',
        'template_dir': 'dirp',
        'file_extension': 'ext',
        'create_link': False,
    }

    @patch('templated_email.TemplateBackend')
    def test_get_templated_mail_returns_response_of_get_email_message(
            self, mocked_backend):
        ret = get_templated_mail(*self.TEST_ARGS)
        self.assertTrue(
            ret is mocked_backend.return_value.get_email_message.return_value)

    @patch('templated_email.TemplateBackend')
    def test_called_get_email_message_from_vanilla_backend(self, mocked_backend):
        get_templated_mail(*self.TEST_ARGS)
        mocked_backend.return_value.get_email_message.assert_called_once()

    @patch('templated_email.TemplateBackend')
    def test_arguments_get_passsed_to_get_email_message(self, mocked_backend):
        get_templated_mail(*self.TEST_ARGS, **self.TEST_KWARGS)

        mocked_backend.assert_called_with(template_prefix='prefix',
                                          template_suffix='suffix')

        get_email_message = mocked_backend.return_value.get_email_message

        kwargs = dict(self.TEST_KWARGS)
        del kwargs['template_dir']
        del kwargs['file_extension']
        get_email_message.assert_called_with(*self.TEST_ARGS, **kwargs)

    @patch('templated_email.TemplateBackend')
    def test_arguments_get_email_message_fallback(self, mocked_backend):
        kwargs = dict(self.TEST_KWARGS)
        del kwargs['template_prefix']
        del kwargs['template_suffix']

        get_templated_mail(*self.TEST_ARGS, **kwargs)

        mocked_backend.assert_called_with(template_prefix=kwargs['template_dir'],
                                          template_suffix=kwargs['file_extension'])

        get_email_message = mocked_backend.return_value.get_email_message

        kwargs['template_prefix'] = kwargs.pop('template_dir')
        kwargs['template_suffix'] = kwargs.pop('file_extension')
        get_email_message.assert_called_with(*self.TEST_ARGS, **kwargs)
