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

Make sure you are reading the correct documentation:

develop branch: https://github.com/vintasoftware/django-templated-email/blob/develop/README.rst

stable pypi/master: https://github.com/vintasoftware/django-templated-email/blob/master/README.rst

Getting going - installation
==============================

Installing::

    pip install django-templated-email

You can add the following to your settings.py (but it works out the box):

.. code-block:: python

    TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django.TemplateBackend'

    # You can use a shortcut version
    TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django'

    # You can also use a class directly
    from templated_email.backends.vanilla_django import TemplateBackend
    TEMPLATED_EMAIL_BACKEND = TemplateBackend


Sending templated emails
==============================

Example usage using vanilla_django TemplateBackend backend

Python to send mail:

.. code-block:: python

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

If you would like finer control on sending the email, you can use **get_templated_email**, which will return a django **EmailMessage** object, prepared using the **vanilla_django** backend:

.. code-block:: python

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

The backend will look in *my_app/templates/templated_email/welcome.email* :

.. code-block:: python

    {% block subject %}My subject for {{username}}{% endblock %}
    {% block plain %}
      Hi {{full_name}},

      You just signed up for my website, using:
          username: {{username}}
          join date: {{signup_date}}

      Thanks, you rock!
    {% endblock %}

If you want to include an HTML part to your emails, simply use the 'html' block :

.. code-block:: python

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

The plain part can also be calculated from the HTML using `html2text <https://pypi.python.org/pypi/html2text>`_. If you don't specify the plain block and `html2text <https://pypi.python.org/pypi/html2text>`_ package is installed, the plain part will be calculated from the HTML part. You can disable this behaviour in settings.py :

.. code-block:: python

    TEMPLATED_EMAIL_AUTO_PLAIN = False

You can globally override the template dir, and file extension using the following variables in settings.py :

.. code-block:: python

    TEMPLATED_EMAIL_TEMPLATE_DIR = 'templated_email/' #use '' for top level template dir, ensure there is a trailing slash
    TEMPLATED_EMAIL_FILE_EXTENSION = 'email'

You can also set a value for **template_prefix** and **template_suffix** for every time you call **send_templated_mail**, if you wish to store a set of templates in a different directory. Remember to include a trailing slash.

Using with `Django Anymail <https://github.com/anymail/django-anymail>`_
=========================================================================

Anymail integrates several transactional email service providers (ESPs) into Django, with a consistent API that lets you use ESP-added features without locking your code to a particular ESP. It supports Mailgun, Postmark, SendGrid, SparkPost and more.

You can use it with django-templated-email, just follow their instructions in their `quick start <https://anymail.readthedocs.io/en/latest/quickstart/>`_ to configure it.

Optionally you can use their custom `EmailMessage <https://anymail.readthedocs.io/en/latest/sending/anymail_additions/#anymail.message.AnymailMessage>`_ class with django-templated-email by using the following settings:

.. code-block:: python

    # This replaces django.core.mail.EmailMessage
    TEMPLATED_EMAIL_EMAIL_MESSAGE_CLASS='anymail.message.AnymailMessage'

    # This replaces django.core.mail.EmailMultiAlternatives
    TEMPLATED_EMAIL_EMAIL_MULTIALTERNATIVES_CLASS='anymail.message.AnymailMessage'


Inline images
==============

You can add inline images to your email using the *InlineImage* class.

First get the image content from a file or a *ImageField*:

.. code-block:: python

    # From a file
    with open('lena.png', 'rb') as lena:
      image = lena.read()

    # From an ImageField
    # Suppose we have this model
    class Company(models.Model):
      logo = models.ImageField()

    image = company.logo.read()

Then create an instance of *InlineImage*:

.. code-block:: python

    from templated_email import InlineImage

    inline_image = InlineImage(filename="lena.png", content=image)

Now pass the object on the context to the template when you send the email.

.. code-block:: python

    send_templated_mail(template_name='welcome',
                        from_email='from@example.com',
                        recipient_list=['to@example.com'],
                        context={'lena_image': inline_image})

Finally in your template add the image on the html template block:

.. code-block:: html

    <img src="{{ lena_image }}">

Note: All *InlineImage* objects you add to the context will be attached to the e-mail, even if they are not used in the template.


Add link to view the email on the web
=====================================

.. code-block:: python

    # Add templated email to INSTALLED_APPS
    INSTALLED_APPS = [
      ...
      'templated_email'
    ]

.. code-block:: python

    # and this to your url patterns
    url(r'^', include('templated_email.urls', namespace='templated_email')),

.. code-block:: python

    # when sending the email use the *create_link* parameter.
    send_templated_mail(
        template_name='welcome', from_email='from@example.com',
        recipient_list=['to@example.com'],
        context={}, create_link=True)

And, finally add the link to your template.

.. code-block:: html

    <!-- With the 'if' the link will only appear on the email. -->
    {% if email_uuid %}
      <!-- Note: you will need to add your site since you will need to access
                 it from the email -->
      You can view this e-mail on the web here:
      <a href="http://www.yoursite.com{% url 'templated_email:show_email' uuid=email_uuid %}">
        here
      </a>
    {% endif %}

Notes:
  - A copy of the rendered e-mail will be stored on the database. This can grow
    if you send too many e-mails. You are responsible for managing it.
  - If you use *InlineImage* all images will be uploaded to your media storage,
    keep that in mind too.


Class Based Views
==================

It's pretty common for emails to be sent after a form is submitted. We include a mixin
to be used with any view that inherit from Django's FormMixin.

In your view add the mixin and the usual Django's attributes:

.. code-block:: python

    from templated_email.generic_views import TemplatedEmailFormViewMixin

    class AuthorCreateView(TemplatedEmailFormViewMixin, CreateView):
        model = Author
        fields = ['name', 'email']
        success_url = '/create_author/'
        template_name = 'authors/create_author.html'

By default the template will have the *form_data* if the form is valid or *from_errors* if the
form is not valid in it's context.

You can view an example `here <tests/generic_views/>`_

Now you can use the following attributes/methods to customize it's behavior:

Attributes:

**templated_email_template_name** (mandatory if you don't implement **templated_email_get_template_names()**):
    String naming the template you want to use for the email.
    ie: templated_email_template_name = 'welcome'.

**templated_email_send_on_success** (default: True):
    This attribute tells django-templated-email to send an email if the form is valid.

**templated_email_send_on_failure** (default: False):
    This attribute tells django-templated-email to send an email if the form is invalid.

**templated_email_from_email** (default: **settings.TEMPLATED_EMAIL_FROM_EMAIL**):
    String containing the email to send the email from.

Methods:

**templated_email_get_template_names(self, valid)** (mandatory if you don't set **templated_email_template_name**):
    If the method returns a string it will use it as the template to render the email. If it returns a list it will send
    the email *only* with the first existing template.

**templated_email_get_recipients(self, form)** (mandatory):
    Return the recipient list to whom the email will be sent to.
    ie:
.. code-block:: python

      def templated_email_get_recipients(self, form):
          return [form.data['email']]

**templated_email_get_context_data(**kwargs)** (optional):
    Use this method to add extra data to the context used for rendering the template. You should get the parent class's context from
    calling super.
    ie:
.. code-block:: python

      def templated_email_get_context_data(self, **kwargs):
          context = super(ThisClassView, self).templated_email_get_context_data(**kwargs)
          # add things to context
          return context

**templated_email_get_send_email_kwargs(self, valid, form)** (optional):
    Add or change the kwargs that will be used to send the e-mail. You should call super to get the default kwargs.
    ie:
.. code-block:: python

    def templated_email_get_send_email_kwargs(valid, form):
      kwargs = super(ThisClassView, self).templated_email_get_send_email_kwargs(valid, form)
      kwargs['bcc'] = ['admin@example.com']
      return kwargs

**templated_email_send_templated_mail(*args, **kwargs)** (optional):
    This method calls django-templated-email's *send_templated_mail* method. You could change this method to use
    a celery's task for example or to handle errors.


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

This is the default backend, and as such requires no special configuration, and will work out of the box. By default it assumes the following settings (should you wish to override them):

.. code-block:: python

    TEMPLATED_EMAIL_TEMPLATE_DIR = 'templated_email/' #Use '' for top level template dir
    TEMPLATED_EMAIL_FILE_EXTENSION = 'email'

For legacy purposes you can specify email subjects in your settings file (but, the preferred method is to use a **{% block subject %}** in your template):

.. code-block:: python

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
