from email.header import Header
import mimetypes

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, \
    DEFAULT_ATTACHMENT_MIME_TYPE, get_connection
from django.template import Context, TemplateDoesNotExist
from django.template.loader import get_template
from django.utils import six
from django.utils.translation import ugettext as _
from templated_email.utils import _get_node, BlockNotFound


class EmailMessageDTE(EmailMessage):

    def _create_attachment(self, filename, content, mimetype=None):
        """
        Converts the filename, content, mimetype triple into a MIME attachment
        object.
        
        Based on code of django 1.6.5 and http://stackoverflow.com/q/15496689
        """
        if mimetype is None:
            mimetype, _ = mimetypes.guess_type(filename)
            if mimetype is None:
                mimetype = DEFAULT_ATTACHMENT_MIME_TYPE
        attachment = self._create_mime_attachment(content, mimetype)
        if filename:
            try:
                filename.encode('ascii')
            except UnicodeEncodeError:
                if six.PY2:
                    filename = filename.encode('utf-8')
                filename = Header(filename, 'utf-8').encode()
            attachment.add_header('Content-Disposition', 'attachment',
                                  filename=filename)
        return attachment


class EmailMultiAlternativesDTE(EmailMultiAlternatives, EmailMessageDTE):
    pass


class EmailRenderException(Exception):
    pass


class TemplateBackend(object):
    """
    Backend which uses Django's
    templates, and django's send_mail function.

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

    ATTACH_SUPPORT = True

    def __init__(self, fail_silently=False,
                 template_prefix=None, template_suffix=None, **kwargs):
        self.template_prefix = template_prefix or getattr(settings, 'TEMPLATED_EMAIL_TEMPLATE_DIR', 'templated_email/')
        self.template_suffix = template_suffix or getattr(settings, 'TEMPLATED_EMAIL_FILE_EXTENSION', 'email')

    def _render_email(self, template_name, context,
                      template_dir=None, file_extension=None):
        response = {}
        errors = {}
        prefixed_template_name = ''.join((template_dir or self.template_prefix, template_name))
        render_context = Context(context, autoescape=False)
        file_extension = file_extension or self.template_suffix
        if file_extension.startswith('.'):
            file_extension = file_extension[1:]
        full_template_name = '%s.%s' % (prefixed_template_name, file_extension)

        try:
            multi_part = get_template(full_template_name)
        except TemplateDoesNotExist:
            multi_part = None

        if multi_part:
            for part in ['subject', 'html', 'plain']:
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
                    raise TemplateDoesNotExist(full_template_name)
                else:
                    plain_part = None

            if plain_part:
                response['plain'] = plain_part.render(render_context)

            if html_part:
                response['html'] = html_part.render(render_context)

        if response == {}:
            raise EmailRenderException("Couldn't render email parts. Errors: %s"
                                       % errors)

        return response

    def get_email_message(self, template_name, context, from_email=None, to=None,
                          cc=None, bcc=None, headers=None,
                          template_prefix=None, template_suffix=None,
                          template_dir=None, file_extension=None, attach=None):

        parts = self._render_email(template_name, context,
                                   template_prefix or template_dir,
                                   template_suffix or file_extension)
        plain_part = 'plain' in parts
        html_part = 'html' in parts

        if 'subject' in parts:
            subject = parts['subject']
        else:
            subject_dict = getattr(settings, 'TEMPLATED_EMAIL_DJANGO_SUBJECTS', {})
            subject_template = subject_dict.get(template_name,
                                                _('%s email subject' % template_name))
            subject = subject_template % context

        if plain_part and not html_part:
            e = EmailMessageDTE(
                subject,
                parts['plain'],
                from_email,
                to,
                cc=cc,
                bcc=bcc,
                headers=headers,
            )

        if html_part and not plain_part:
            e = EmailMessageDTE(
                subject,
                parts['html'],
                from_email,
                to,
                cc=cc,
                bcc=bcc,
                headers=headers,
            )
            e.content_subtype = 'html'

        if plain_part and html_part:
            e = EmailMultiAlternativesDTE(
                subject,
                parts['plain'],
                from_email,
                to,
                cc=cc,
                bcc=bcc,
                headers=headers,
            )
            e.attach_alternative(parts['html'], 'text/html')

        if attach is not None:
            for f in attach:
                e.attach(f.get('filename'), f.get('content'), f.get('mimetype'))

        return e

    def send(self, template_name, from_email, recipient_list, context,
             cc=None, bcc=None,
             fail_silently=False,
             headers=None,
             template_prefix=None, template_suffix=None,
             template_dir=None, file_extension=None,
             auth_user=None, auth_password=None,
             connection=None, attach=None, **kwargs):

        connection = connection or get_connection(username=auth_user,
                                                  password=auth_password,
                                                  fail_silently=fail_silently)

        e = self.get_email_message(template_name, context, from_email=from_email,
                                   to=recipient_list, cc=cc, bcc=bcc, headers=headers,
                                   template_prefix=template_prefix,
                                   template_suffix=template_suffix,
                                   template_dir=template_dir,
                                   file_extension=file_extension, attach=attach)

        e.connection = connection

        try:
            e.send(fail_silently)
        except NameError:
            raise EmailRenderException("Couldn't render plain or html parts")

        return e.extra_headers.get('Message-Id', None)
