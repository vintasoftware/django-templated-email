from django.conf import settings
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

def get_connection(backend=None, template_prefix=None, fail_silently=False, **kwargs):
    """Load a templated e-mail backend and return an instance of it.

    If backend is None (default) settings.TEMPLATED_EMAIL_BACKEND is used.

    Both fail_silently and other keyword arguments are used in the
    constructor of the backend.
    """
    # This method is mostly a copy of the backend loader present in django.core.mail.get_connection
    template_prefix = template_prefix or getattr(settings,'TEMPLATED_EMAIL_TEMPLATE_DIR','templated_email/')
    path = backend or getattr(settings,'TEMPLATED_EMAIL_BACKEND','templated_email.backends.vanilla_django.TemplateBackend')
    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(('Error importing templated email backend module %s: "%s"'
                                    % (mod_name, e)))
    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured(('Module "%s" does not define a '
                                    '"%s" class' % (mod_name, klass_name)))
    return klass(fail_silently=fail_silently, template_prefix=template_prefix, **kwargs)


def send_templated_mail(template_name, from_email, recipient_list, context, cc=[], bcc=[], fail_silently=False, connection=None, headers = {}):
    """Easy wrapper for sending a templated email to a recipient list. 

    Final behaviour of sending depends on the currently selected engine.
    See BackendClass.send.__doc__
    """ 
    connection = connection or get_connection()
    return connection.send(template_name, from_email, recipient_list, context, cc, bcc, fail_silently, headers=headers)
