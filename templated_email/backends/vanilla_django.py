from django.conf import settings
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.template import Context, TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from templated_email.utils import _get_node, BlockNotFound

class EmailRenderException(Exception):
    pass

class TemplateBackend:
    """
    Backend which uses Django's templates, and django's send_mail function.
    
    Heavily inspired by http://stackoverflow.com/questions/2809547/creating-email-templates-with-django

    Default / preferred behaviour works like so:
        templates named 
            templated_email/<template_name>.email

        {% block subject %} declares the subject
        {% block plain %} declares text/plain
        {% block html %} declares text/html

    Legacy behaviour loads from:
        text/plain part:
            templated_email/<template_name>.txt
        text/html part:
            templated_email/<template_name>.html

        Subjects for email templates can be configured in one of two ways:

        * If you are using internationalisation, you can simply create entries for
          "<template_name> email subject" as a msgid in your PO file

        * Using a dictionary in settings.py, TEMPLATED_EMAIL_DJANGO_SUBJECTS, 
          for e.g.: 
          TEMPLATED_EMAIL_DJANGO_SUBJECTS = {
            'welcome':'Welcome to my website',
          }

    Subjects are templatable using the context, i.e. A subject
    that resolves to 'Welcome to my website, %(username)s', requires that
    the context passed in to the send() method contains 'username' as one
    of it's keys
    """

    def __init__(self, 
            fail_silently=False, 
            template_prefix=getattr(settings,'TEMPLATED_EMAIL_TEMPLATE_DIR','templated_email/'), 
            template_suffix=getattr(settings,'TEMPLATED_EMAIL_FILE_EXTENSION','email'),
            **kwargs):
        self.template_prefix = template_prefix
        self.template_suffix = template_suffix

    def _render_email(self,template_name, context):
        response = {}
        errors = {}
        prefixed_template_name=''.join((self.template_prefix,template_name))
        render_context = Context(context, autoescape=False)

        try:
            multi_part = get_template('%s.%s' % (prefixed_template_name, self.template_suffix))
        except TemplateDoesNotExist:
            multi_part = None

        if multi_part:
            for part in ['subject','html','plain']:
                try:
                    response[part] = _get_node(multi_part, render_context, name=part)
                except BlockNotFound, error:
                    errors[part] = error
        else:
            try:
                html_part = get_template('%s.html' % prefixed_template_name)
            except TemplateDoesNotExist:
                html_part = None

            try:
                plain_part = get_template('%s.txt' % prefixed_template_name)
            except TemplateDoesNotExist:
                if not html_part:
                    raise TemplateDoesNotExist('%s.txt' % prefixed_template_name)
                else:
                    plain_part = None

            if plain_part:
                response['plain'] = plain_part.render(render_context)

            if html_part:
                response['html'] = html_part.render(render_context)

        if response == {}:
            raise EmailRenderException("Couldn't render email parts. Errors: %s" % errors)

        return response

    def send(self, template_name, from_email, recipient_list, context, cc=[], bcc=[], fail_silently=False, headers={}):
        parts = self._render_email(template_name, context)
        plain_part = parts.has_key('plain')
        html_part = parts.has_key('html')

        subject = parts.get('subject',
                    getattr(
                        settings,'TEMPLATED_EMAIL_DJANGO_SUBJECTS',{}
                    ).get(
                        template_name,
                        _('%s email subject' % template_name)
                    ) % context
                )
        
        if plain_part and not html_part:
            e=EmailMessage(
                subject,
                parts['plain'],
                from_email,
                recipient_list,
                cc = cc,
                bcc = bcc,
                headers = headers,
            )
            e.send(fail_silently)

        if html_part and not plain_part:
            e=EmailMessage(
                subject,
                parts['html'],
                from_email,
                recipient_list,
                cc = cc,
                bcc = bcc,
                headers = headers,
            )
            e.content_subtype = 'html'
            e.send(fail_silently)

        if plain_part and html_part:
            e=EmailMultiAlternatives(
                subject,
                parts['plain'],
                from_email,
                recipient_list,
                cc = cc,
                bcc = bcc,
                headers = headers,
            )
            e.attach_alternative(parts['html'],'text/html')
            e.send(fail_silently)
        
        return e.extra_headers.get('Message-Id',None)

