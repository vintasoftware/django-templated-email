import vanilla_django
from greatape import MailChimpSTS
from django.conf import settings
from django.utils.translation import ugettext as _

class TemplateBackend(vanilla_django.TemplateBackend):
    def __init__(self, *args, **kwargs):
        vanilla_django.TemplateBackend.__init__(self, *args, **kwargs)
        self.connection = MailChimpSTS(settings.MAILCHIMP_API_KEY, debug=True)
        
    def send(self, template_name, from_email, recipient_list, context, cc=[], bcc=[], fail_silently=False, headers={}):
        config = getattr(settings,'TEMPLATED_EMAIL_MAILCHIMP',{}).get(template_name,{})
        parts = self._render_email(template_name, context)
        params={
            'message':{
                'subject':config.get('subject',_('%s email subject' % template_name)) % context,
                'html':parts.get('html',''),
                'text':parts.get('plain',''),
                'from_name':' '.join(from_email.split(' ')[:-1]) or 'Nobody',
                'from_email':from_email,
                'to_email':recipient_list,
            },
            'track_opens':config.get('track_opens',False),
            'track_clicks':config.get('track_clicks',False),
            'tags':config.get('tags',[]),
        }
        if cc:
            params['message']['cc_email'] = ', '.join(cc)
        if bcc:
            params['message']['bcc_email'] = ', '.join(bcc)
        self.connection.SendEmail(params)
