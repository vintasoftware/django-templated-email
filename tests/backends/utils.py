from django.test import override_settings


class TempalteBackendBaseMixin(object):

    @override_settings(TEMPLATED_EMAIL_TEMPLATE_DIR='test_prefix')
    def test_uses_prefix_from_config(self):
        backend = self.template_backend_klass()
        self.assertEqual(backend.template_prefix, 'test_prefix')

    @override_settings(TEMPLATED_EMAIL_FILE_EXTENSION='test_suffix')
    def test_uses_suffix_from_config(self):
        backend = self.template_backend_klass()
        self.assertEqual(backend.template_suffix, 'test_suffix')

    def test_override_prefix_from_config(self):
        backend = self.template_backend_klass(template_prefix='test_prefix')
        self.assertEqual(backend.template_prefix, 'test_prefix')

    def test_override_suffix_from_config(self):
        backend = self.template_backend_klass(template_suffix='test_suffix')
        self.assertEqual(backend.template_suffix, 'test_suffix')
