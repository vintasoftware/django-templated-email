from django.urls import re_path

from templated_email.views import ShowEmailView

app_name = 'templated_email'
urlpatterns = [
    re_path(r'^email/(?P<uuid>([a-f\d]{32})|([a-f\d]{8}(-[a-f\d]{4}){3}-[a-f\d]{12}))/$', ShowEmailView.as_view(), name='show_email'),
]
