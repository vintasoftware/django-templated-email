from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.utils.translation import ugettext as _

from postageapp import PostageApp

from . import HeaderNotSupportedException

class TemplateBackend:
    """
    Backend which uses PostageApp to send templated emails

    Requires python-postageapp:
    pip install -e git://github.com/bradwhittington/python-postageapp.git#egg=postageapp

    Relies on the following settings:
    POSTAGEAPP_API_KEY = '<your api key>'

    (Additionally it will check for EMAIL_POSTAGEAPP_API_KEY per
    django-postageapp)
    """

    def __init__(self, fail_silently=False, api_key=None, **kwargs):
        api_key = api_key or getattr(settings,'POSTAGEAPP_API_KEY',getattr(settings,'EMAIL_POSTAGEAPP_API_KEY',None))
        if api_key:
            self.conn = PostageApp(api_key)
        else:
            raise ImproperlyConfigured('You need to provide POSTAGEAPP_API_KEY or EMAIL_POSTAGEAPP_API_KEY in your Django settings file') 

    def send(self, template_name, from_email, recipient_list, context, cc=[], bcc=[], fail_silently=False, headers={}):
        if cc != [] or bcc != []:
            raise HeaderNotSupportedException("PostageApp doesn't currently support CC, or BCC")
        try:
            result = self.conn.send_message(
                recipients=recipient_list,
                from_email=from_email,
                template=template_name,
                variables=context,
                headers=headers
            )
        except Exception, e:
            if not fail_silently:
                raise

        return result
