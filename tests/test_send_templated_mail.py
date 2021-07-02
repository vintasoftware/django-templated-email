from django.test import TestCase

from mock import patch, Mock

from templated_email import send_templated_mail


class SendTemplatedMailTestCase(TestCase):
    TEST_ARGS = ['a_template_name', 'from@example.com', ['to@example.com'],
                 {'context': 'content'}]
    TEST_KWARGS = {
        'cc': ['cc@example.com'],
        'bcc': ['bcc@example.com'],
        'fail_silently': True,
        'headers': {'A_HEADER': 'foo'},
        'template_prefix': 'prefix',
        'template_suffix': 'suffix',
        'something': 'else',
        'connection': None,
        'create_link': False,
    }

    def test_send_templated_mail_returns_send_response(self):
        mock_template_backend = Mock()
        ret = send_templated_mail(*self.TEST_ARGS, template_backend=mock_template_backend,
                                  **self.TEST_KWARGS)
        self.assertTrue(ret is mock_template_backend.send.return_value)

    def test_with_template_backend_in_args(self):
        mock_template_backend = Mock()
        send_templated_mail(*self.TEST_ARGS, template_backend=mock_template_backend,
                            **self.TEST_KWARGS)

        kwargs = dict(self.TEST_KWARGS)
        del kwargs['template_prefix']
        del kwargs['template_suffix']
        mock_template_backend.send.assert_called_with(*self.TEST_ARGS, **kwargs)

    @patch('templated_email.get_default_template_backend')
    def test_without_template_backend_in_args(self, mocked_get_default_template_backend):
        send_templated_mail(*self.TEST_ARGS, **self.TEST_KWARGS)

        mocked_get_default_template_backend.assert_called_with(template_prefix='prefix',
                                                 template_suffix='suffix')

        mock_template_backend = mocked_get_default_template_backend.return_value
        kwargs = dict(self.TEST_KWARGS)
        del kwargs['template_prefix']
        del kwargs['template_suffix']
        mock_template_backend.send.assert_called_with(*self.TEST_ARGS, **kwargs)

    def test_with_connection_in_args(self):
        mock_connection = Mock()
        mock_template_backend = Mock()
        kwargs = dict(self.TEST_KWARGS)
        del kwargs['connection']
        send_templated_mail(*self.TEST_ARGS, connection=mock_connection,
                            template_backend=mock_template_backend, **kwargs)

        del kwargs['template_prefix']
        del kwargs['template_suffix']
        mock_connection.send.assert_called_with(*self.TEST_ARGS, **kwargs)

    @patch('templated_email.get_default_connection')
    def test_without_connection_in_args(self, mocked_get_connection):
        send_templated_mail(*self.TEST_ARGS, **self.TEST_KWARGS)

        mocked_get_connection.assert_called_with(template_prefix='prefix',
                                                 template_suffix='suffix')

        mock_connection = mocked_get_connection.return_value
        kwargs = dict(self.TEST_KWARGS)
        del kwargs['template_prefix']
        del kwargs['template_suffix']
        mock_connection.send.assert_called_with(*self.TEST_ARGS, **kwargs)
