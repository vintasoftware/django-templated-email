import logging

from django.conf import settings
from django.utils.translation import ugettext as _

import mandrill
import vanilla_django


log = logging.getLogger(__name__)


class TemplateBackend(vanilla_django.TemplateBackend):
    def __init__(self, *args, **kwargs):
        vanilla_django.TemplateBackend.__init__(self, *args, **kwargs)
        self.client = mandrill.Mandrill(settings.MANDRILL_API_KEY)

    def send(self, template_name, from_email, recipient_list, context, cc=None,
            bcc=None, fail_silently=False, headers=None, template_prefix=None,
            template_suffix=None, template_dir=None, file_extension=None,
            extra_params=None, **kwargs):

        config = getattr(settings, 'TEMPLATED_EMAIL_MANDRILL', {}).get(template_name, {})
        parts = self._render_email(template_name, context,
                                   template_dir=template_prefix or template_dir,
                                   file_extension=template_suffix or file_extension)
        message = {
            'subject': config.get('subject', _('%s email subject' % template_name)) % context,
            'html': parts.get('html', ''),
            'text': parts.get('plain', ''),
            'from_name': ' '.join(from_email.split(' ')[:-1]) or 'Nobody',
            'from_email': from_email,
            'to': recipient_list,
            'track_opens': config.get('track_opens', False),
            'track_clicks': config.get('track_clicks', False),
            'tags': config.get('tags', []),
        }
        if cc:
            message['cc_address'] = ', '.join(cc)
        if bcc:
            message['bcc_address'] = ', '.join(bcc)
        if headers:
            message['headers']: headers
        if extra_params:
            message.update(extra_params)

        try:
            self.client.messages.send(message=message, **kwargs)
        except mandrill.Error as e:
            log.error(e)
            if not fail_silently:
                raise

