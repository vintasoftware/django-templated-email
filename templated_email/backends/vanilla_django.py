from django.conf import settings
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.template import Context, TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.translation import ugettext as _

class TemplateBackend:
    """
    Backend which uses Django's templates, and django's send_mail function.
    
    Heavily inspired by http://stackoverflow.com/questions/2809547/creating-email-templates-with-django
 
    Templates are loaded from (by default):
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

    Additionally subjects are templatable using the context, i.e. A subject
    that resolves to 'Welcome to my website, %(username)s', requires that
    the context passed in to the send() method contains 'username' as one
    of it's keys
    """

    def __init__(self, fail_silently=False, template_prefix='templated_email/', **kwargs):
        self.template_prefix = template_prefix

    def send(self, template_name, from_email, recipient_list, context, fail_silently=False):
        subject = getattr(
                        settings,'TEMPLATED_EMAIL_DJANGO_SUBJECTS',{}
                    ).get(
                        template_name,
                        _('%s email subject' % template_name)
                    ) % context

        prefixed_template_name=''.join((self.template_prefix,template_name))

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

        #TODO: Should we WARN if we only found an html part?

        render_context = Context(context)

        #TODO: Handle bundling in assets/attachments
        
        if plain_part and not html_part:
            e=EmailMessage(
                subject,
                plain_part.render(render_context),
                from_email,
                recipient_list,
            )
            e.send(fail_silently)

        if html_part and not plain_part:
            e=EmailMessage(
                subject,
                html_part.render(render_context),
                from_email,
                recipient_list,
            )
            e.content_subtype = 'html'
            e.send(fail_silently)

        if plain_part and html_part:
            e=EmailMultiAlternatives(
                subject,
                plain_part.render(render_context),
                from_email,
                recipient_list,
            )
            e.attach_alternative(html_part.render(render_context),'text/html')
            e.send(fail_silently)

