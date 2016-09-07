==============================
Django-Templated-Email
==============================

|GitterBadge|_ |PypiversionBadge|_ |PythonVersionsBadge|_ |LicenseBadge|_

:Info: A Django oriented templated email sending class
:Author: Bradley Whittington (http://github.com/bradwhittington, http://twitter.com/darb)
:Tests: |TravisBadge|_ |CoverageBadge|_


Overview
=================
django-templated-email is oriented towards sending templated emails.
The library supports template inheritance, adding cc'd and bcc'd recipients,
configurable template naming and location.

The send_templated_email method can be thought of as the render_to_response
shortcut for email.

Getting going - installation
==============================

Installing::

    pip install django-templated-email

You can add the following to your settings.py (but it works out the box)::

    TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django.TemplateBackend'

    # You can use a shortcut version
    TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django'

    # You can also use a class directly
    from templated_email.backends.vanilla_django import TemplateBackend
    TEMPLATED_EMAIL_BACKEND = TemplateBackend


Sending templated emails
==============================

Example usage using vanilla_django TemplateBackend backend

Python to send mail::

    from templated_email import send_templated_mail
    send_templated_mail(
            template_name='welcome',
            from_email='from@example.com',
            recipient_list=['to@example.com'],
            context={
                'username':request.user.username,
                'full_name':request.user.get_full_name(),
                'signup_date':request.user.date_joined
            },
            # Optional:
            # cc=['cc@example.com'],
            # bcc=['bcc@example.com'],
            # headers={'My-Custom-Header':'Custom Value'},
            # template_prefix="my_emails/",
            # template_suffix="email",
    )

If you would like finer control on sending the email, you can use **get_templated_email**, which will return a django **EmailMessage** object, prepared using the **vanilla_django** backend::

    from templated_email import get_templated_mail
    get_templated_mail(
            template_name='welcome',
            from_email='from@example.com',
            to=['to@example.com'],
            context={
                'username':request.user.username,
                'full_name':request.user.get_full_name(),
                'signup_date':request.user.date_joined
            },
            # Optional:
            # cc=['cc@example.com'],
            # bcc=['bcc@example.com'],
            # headers={'My-Custom-Header':'Custom Value'},
            # template_prefix="my_emails/",
            # template_suffix="email",
    )

You can also **cc** and **bcc** recipients using **cc=['example@example.com']**.

Your template
-------------

The templated_email/ directory needs to be the templates directory.

The backend will look in *my_app/templates/templated_email/welcome.email* ::

    {% block subject %}My subject for {{username}}{% endblock %}
    {% block plain %}
      Hi {{full_name}},

      You just signed up for my website, using:
          username: {{username}}
          join date: {{signup_date}}

      Thanks, you rock!
    {% endblock %}

If you want to include an HTML part to your emails, simply use the 'html' block ::

    {% block html %}
      <p>Hi {{full_name}},</p>

      <p>You just signed up for my website, using:
          <dl>
            <dt>username</dt><dd>{{username}}</dd>
            <dt>join date</dt><dd>{{signup_date}}</dd>
          </dl>
      </p>

      <p>Thanks, you rock!</p>
    {% endblock %}

The plain part can also be calculated from the HTML using `html2text <https://pypi.python.org/pypi/html2text>`_. If you don't specify the plain block and `html2text <https://pypi.python.org/pypi/html2text>`_ package is installed, the plain part will be calculated from the HTML part. You can disable this behaviour in settings.py ::

    TEMPLATED_EMAIL_AUTO_PLAIN = False

You can globally override the template dir, and file extension using the following variables in settings.py ::

    TEMPLATED_EMAIL_TEMPLATE_DIR = 'templated_email/' #use '' for top level template dir, ensure there is a trailing slash
    TEMPLATED_EMAIL_FILE_EXTENSION = 'email'

You can also set a value for **template_prefix** and **template_suffix** for every time you call **send_templated_mail**, if you wish to store a set of templates in a different directory. Remember to include a trailing slash.

Using with `Django Anymail <https://github.com/anymail/django-anymail>`_
=========================================================================

Anymail integrates several transactional email service providers (ESPs) into Django, with a consistent API that lets you use ESP-added features without locking your code to a particular ESP. It supports Mailgun, Postmark, SendGrid, SparkPost and more.

You can use it with django-templated-email, just follow their instructions in their `quick start <https://anymail.readthedocs.io/en/latest/quickstart/>`_ to configure it.

Optionally you can use their custom `EmailMessage <https://anymail.readthedocs.io/en/latest/sending/anymail_additions/#anymail.message.AnymailMessage>`_ class with django-templated-email by using the following settings:

    # This replaces django.core.mail.EmailMessage
    TEMPLATED_EMAIL_EMAIL_MESSAGE_CLASS='anymail.message.AnymailMessage'

    # This replaces django.core.mail.EmailMultiAlternatives
    TEMPLATED_EMAIL_EMAIL_MULTIALTERNATIVES_CLASS='anymail.message.AnymailMessage'


Future Plans
=============

See https://github.com/vintasoftware/django-templated-email/issues?state=open

Using django_templated_email in 3rd party applications
=======================================================

If you would like to use django_templated_email to handle mail in a reusable application, you should note that:

* Your calls to **send_templated_mail** should set a value for **template_dir**, so you can keep copies of your app-specific templates local to your app (although the loader will find your email templates if you store them in *<your app>/templates/templated_email*, if **TEMPLATED_EMAIL_TEMPLATE_DIR** has not been overidden)
* If you do (and you should) set a value for **template_dir**, remember to include a trailing slash, i.e. *'my_app_email/'*
* The deployed app may use a different backend which doesn't use the django templating backend, and as such make a note in your README warning developers that if they are using django_templated_email already, with a different backend, they will need to ensure their email provider can send all your templates (ideally enumerate those somewhere convenient)

Notes on specific backends
==============================

Using vanilla_django
--------------------------

This is the default backend, and as such requires no special configuration, and will work out of the box. By default it assumes the following settings (should you wish to override them)::

    TEMPLATED_EMAIL_TEMPLATE_DIR = 'templated_email/' #Use '' for top level template dir
    TEMPLATED_EMAIL_FILE_EXTENSION = 'email'

For legacy purposes you can specify email subjects in your settings file (but, the preferred method is to use a **{% block subject %}** in your template)::

    TEMPLATED_EMAIL_DJANGO_SUBJECTS = {
        'welcome':'Welcome to my website',
    }

Additionally you can call **send_templated_mail** and optionally override the following parameters::

    template_prefix='your_template_dir/'  # Override where the method looks for email templates (alternatively, use template_dir)
    template_suffix='email'               # Override the file extension of the email templates (alternatively, use file_extension)
    cc=['fubar@example.com']              # Set a CC on the mail
    bcc=['fubar@example.com']             # Set a BCC on the mail
    template_dir='your_template_dir/'     # Override where the method looks for email templates
    connection=your_connection            # Takes a django mail backend connection, created using **django.core.mail.get_connection**
    auth_user='username'                  # Override the user that the django mail backend uses, per **django.core.mail.send_mail**
    auth_password='password'              # Override the password that the django mail backend uses, per **django.core.mail.send_mail**

.. _Django: http://djangoproject.com
.. |GitterBadge| image:: https://badges.gitter.im/vintasoftware/django-templated-email.svg
.. _GitterBadge: https://gitter.im/vintasoftware/django-templated-email?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
.. |TravisBadge| image:: https://travis-ci.org/vintasoftware/django-templated-email.svg?branch=develop
.. _TravisBadge: https://travis-ci.org/vintasoftware/django-templated-email
.. |CoverageBadge| image:: https://coveralls.io/repos/github/vintasoftware/django-templated-email/badge.svg?branch=develop
.. _CoverageBadge: https://coveralls.io/github/vintasoftware/django-templated-email?branch=develop
.. |PypiversionBadge| image:: https://img.shields.io/pypi/v/django-templated-email.svg
.. _PypiversionBadge: https://pypi.python.org/pypi/django-templated-email
.. |PythonVersionsBadge| image:: https://img.shields.io/pypi/pyversions/django-templated-email.svg
.. _PythonVersionsBadge: https://pypi.python.org/pypi/django-templated-email
.. |LicenseBadge| image:: https://img.shields.io/pypi/l/django-templated-email.svg
.. _LicenseBadge: https://github.com/vintasoftware/django-templated-email/blob/develop/LICENSE
