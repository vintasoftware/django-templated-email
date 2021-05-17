from django.conf.urls import include
from django.urls import re_path

urlpatterns = [
    re_path(r'^', include('templated_email.urls', namespace='templated_email')),
]
