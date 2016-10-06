from django.conf.urls import url, include
from django.conf import settings
from django.views import static

urlpatterns = [
    url(r'^', include('templated_email.urls', namespace='templated_email')),
]
