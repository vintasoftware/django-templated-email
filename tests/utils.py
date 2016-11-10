import mock


class MockedNetworkTestCaseMixin(object):
    # getfqdn can be too slow, mock it for speed.
    # See: https://code.djangoproject.com/ticket/24380
    @classmethod
    def setUpClass(cls):
        cls.getfqdn_patcher = mock.patch(
            'django.core.mail.utils.socket.getfqdn',
            return_value='vinta.local')
        cls.getfqdn_patcher.start()
        super(MockedNetworkTestCaseMixin, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.getfqdn_patcher.stop()
        super(MockedNetworkTestCaseMixin, cls).tearDownClass()
