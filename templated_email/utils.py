from functools import partial

from django.utils.module_loading import import_string
from django.conf import settings

import six


def _get_klass_from_config(config_variable, default):
    klass_path = getattr(settings, config_variable, default)
    if isinstance(klass_path, six.string_types):
        klass_path = import_string(klass_path)

    return klass_path


get_emailmessage_klass = partial(
    _get_klass_from_config,
    'TEMPLATED_EMAIL_EMAIL_MESSAGE_CLASS',
    'django.core.mail.EmailMessage'
)

get_emailmultialternatives_klass = partial(
    _get_klass_from_config,
    'TEMPLATED_EMAIL_EMAIL_MULTIALTERNATIVES_CLASS',
    'django.core.mail.EmailMultiAlternatives',
)
