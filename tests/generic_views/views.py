from django.views.generic.edit import CreateView

from templated_email.generic_views import TemplatedEmailFormViewMixin
from tests.generic_views.models import Author


# This view send a welcome email to the author
class AuthorCreateView(TemplatedEmailFormViewMixin, CreateView):
    model = Author
    fields = ['name', 'email']
    templated_email_template_name = 'welcome'
    template_name = 'authors/create_author.html'
    success_url = '/create_author/'

    def templated_email_get_recipients(self, form):
        return [form.data['email']]
