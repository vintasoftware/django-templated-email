from django.test import TestCase, RequestFactory, override_settings
from django.core.exceptions import ImproperlyConfigured
from django.core import mail

import mock

from templated_email.generic_views import TemplatedEmailFormViewMixin
from tests.generic_views.views import AuthorCreateView
from tests.generic_views.models import Author
from tests.utils import MockedNetworkTestCaseMixin


class TemplatedEmailFormViewMixinUnitTestCase(TestCase):
    def setUp(self):
        self.mixin_object = TemplatedEmailFormViewMixin()

    def test_templated_email_get_template_names_raises_exception(self):
        self.assertRaises(ImproperlyConfigured,
                          self.mixin_object.templated_email_get_template_names,
                          valid=True)
        self.assertRaises(ImproperlyConfigured,
                          self.mixin_object.templated_email_get_template_names,
                          valid=False)

    def test_templated_email_get_template_names_with_template_name(self):
        self.mixin_object.templated_email_template_name = 'template_name'
        self.assertEquals(
            self.mixin_object.templated_email_get_template_names(valid=True),
            ['template_name']
        )
        self.assertEquals(
            self.mixin_object.templated_email_get_template_names(valid=False),
            ['template_name']
        )

    def test_templated_email_get_context_data(self):
        context = self.mixin_object.templated_email_get_context_data()
        self.assertEqual(context, {})
        context = self.mixin_object.templated_email_get_context_data(foo='bar')
        self.assertEqual(context, {'foo': 'bar'})

    def test_templated_email_get_recipients(self):
        self.assertRaises(NotImplementedError,
                          self.mixin_object.templated_email_get_recipients,
                          form=None)

    @mock.patch.object(TemplatedEmailFormViewMixin,
                       'templated_email_get_template_names',
                       return_value=['template'])
    @mock.patch.object(TemplatedEmailFormViewMixin,
                       'templated_email_get_recipients',
                       return_value=['foo@example.com'])
    def test_templated_email_get_send_email_kwargs_valid(
            self,
            mocked_get_templated_email_recipients,
            mocked_get_templated_email_template_names):
        class FakeForm(object):
            data = 'foo'
        form = FakeForm()
        kwargs = self.mixin_object.templated_email_get_send_email_kwargs(
            valid=True, form=form)
        self.assertEquals(len(kwargs), 4)
        self.assertEquals(kwargs['template_name'], ['template'])
        self.assertEquals(kwargs['from_email'], None)
        self.assertEquals(kwargs['recipient_list'], ['foo@example.com'])
        self.assertEquals(kwargs['context'], {'form_data': 'foo'})

    @mock.patch.object(TemplatedEmailFormViewMixin,
                       'templated_email_get_template_names',
                       return_value=['template'])
    @mock.patch.object(TemplatedEmailFormViewMixin,
                       'templated_email_get_recipients',
                       return_value=['foo@example.com'])
    def test_templated_email_get_send_email_kwargs_not_valid(
            self,
            mocked_get_templated_email_recipients,
            mocked_get_templated_email_template_names):
        class FakeForm(object):
            errors = 'errors foo'
        form = FakeForm()
        kwargs = self.mixin_object.templated_email_get_send_email_kwargs(
            valid=False, form=form)
        self.assertEquals(len(kwargs), 4)
        self.assertEquals(kwargs['template_name'], ['template'])
        self.assertEquals(kwargs['from_email'], None)
        self.assertEquals(kwargs['recipient_list'], ['foo@example.com'])
        self.assertEquals(kwargs['context'], {'form_errors': 'errors foo'})


class TemplatedEmailFormViewMixinTestCase(MockedNetworkTestCaseMixin, TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.good_request = self.factory.post(
            '/doesnt-matter/',
            data={'email': 'author@vinta.com.br', 'name': 'Andre'}
        )
        self.bad_request = self.factory.post(
            '/doesnt-matter/',
            data={'email': 'this_is_not_an_email', 'name': 'Andre'}
        )

    def test_form_valid_with_send_on_success(self):
        response = AuthorCreateView.as_view()(self.good_request)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Author.objects.count(), 1)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].alternatives[0][0].strip(),
                          'Andre - author@vinta.com.br')

    def test_form_valid_with_send_on_success_false(self):
        default_value = AuthorCreateView.templated_email_send_on_success
        AuthorCreateView.templated_email_send_on_success = False
        response = AuthorCreateView.as_view()(self.good_request)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Author.objects.count(), 1)
        self.assertEquals(len(mail.outbox), 0)
        AuthorCreateView.templated_email_send_on_success = default_value

    def test_form_invalid_with_not_send_on_failure(self):
        response = AuthorCreateView.as_view()(self.bad_request)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Author.objects.count(), 0)
        self.assertEquals(len(mail.outbox), 0)

    def test_form_invalid_with_send_on_failure(self):
        default_value = AuthorCreateView.templated_email_send_on_failure
        AuthorCreateView.templated_email_send_on_failure = True
        response = AuthorCreateView.as_view()(self.bad_request)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Author.objects.count(), 0)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].alternatives[0][0].strip(),
                          '* Enter a valid email address.')
        AuthorCreateView.templated_email_send_on_failure = default_value

    @override_settings(TEMPLATED_EMAIL_FROM_EMAIL='from@vinta.com.br')
    def test_from_email(self):
        AuthorCreateView.as_view()(self.good_request)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].from_email, 'from@vinta.com.br')

    def test_from_email_with_templated_email_from_email(self):
        default_value = AuthorCreateView.templated_email_from_email
        AuthorCreateView.templated_email_from_email = 'from2@vinta.com.br'
        AuthorCreateView.as_view()(self.good_request)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].from_email, 'from2@vinta.com.br')
        AuthorCreateView.templated_email_from_email = default_value
