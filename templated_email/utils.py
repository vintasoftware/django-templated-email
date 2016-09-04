from django.utils.module_loading import import_string
from django.conf import settings

import six


def get_emailmessage_klass():
    klass_path = getattr(settings,
                         'TEMPLATED_EMAIL_EMAIL_MESSAGE_CLASS',
                         'django.core.mail.EmailMessage')
    if isinstance(klass_path, six.string_types):
        klass_path = import_string(klass_path)

    return klass_path


def get_emailmultialternatives_klass():
    klass_path = getattr(settings,
                         'TEMPLATED_EMAIL_EMAIL_MULTIALTERNATIVES_CLASS',
                         'django.core.mail.EmailMultiAlternatives')
    if isinstance(klass_path, six.string_types):
        klass_path = import_string(klass_path)

    return klass_path
