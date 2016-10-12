from django.conf.urls import url

from templated_email.views import ShowEmailView

app_name = 'templated_email'
urlpatterns = [
    url(r'^email/(?P<uuid>.*)/$', ShowEmailView.as_view(), name='show_email'),
]
