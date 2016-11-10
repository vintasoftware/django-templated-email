from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('templated_email.urls', namespace='templated_email')),
]
