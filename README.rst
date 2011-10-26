==========
Django-Templated-Email
==========
:Info: A Django oriented templated email sending class
:Author: Bradley Whittington (http://github.com/bradwhittington, http://twitter.com/darb)

Overview
=================
django-templated-email is oriented towards sending templated emails 
intended for use with transactional mailers (ala mailchimp, silverpop, 
etc.), but currently comes out of the box with a backend class which 
uses django's templating system, and django's core.mail functions.

The send_templated_email method can be thought of as the render_to_response
shortcut for email.

Getting going - installation
=============

Installing::

    pip install django-templated-email

You can add the following to your settings.py (but it works out the box)::

    TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django.TemplateBackend'

    # For the django back-end specifically
    TEMPLATED_EMAIL_DJANGO_SUBJECTS = {
        'welcome':'Welcome to my website',
    }

Getting going - sending your template emails
=============

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
            headers={'My-Custom-Header':'Custom Value'}
    )

**Your template**
The backend will look in *templated_email/welcome.email* ::

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


You can override the template dir, and file extension using the following variables in settings.py ::

    TEMPLATED_EMAIL_TEMPLATE_DIR = 'templated_email/' #use '' for top level template dir
    TEMPLATED_EMAIL_FILE_EXTENSION = 'email'


**Legacy Behaviour**
The 0.2.x version of the library looked in django template directories/loaders 
for *templated_email/welcome.txt* ::

    Hey {{full_name}},

    You just signed up for my website, using:
        username: {{username}}
        join date: {{signup_date}}

    Thanks, you rock!

It will use *templated_email/welcome.html* for the html part 
of the email allowing you to make it so much pretty. It is plausible
that one day there will be support for attachments and inline mime / images

Using PostageApp:
=============

To use the PostageApp (http://postageapp.com) send method, you will need to install python-postageapp::

    pip install -e git://github.com/bradwhittington/python-postageapp.git#egg=postageapp

And add the following to your settings.py::

    TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.postageapp_backend.TemplateBackend'

    POSTAGEAPP_API_KEY = 'yourapikey'

    #If you are already using django-postageapp:

    EMAIL_POSTAGEAPP_API_KEY = POSTAGEAPP_API_KEY

Using MAILCHIMP STS:
=============

To use the MailChimp STS send method, you will need to install mailsnake (please note, until the main mailsnake has STS support, you need to use my fork)::

    pip install -e git://github.com/bradwhittington/mailsnake.git#egg=mailsnake

And add the following to your settings.py::

    TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.mailchimp_sts.TemplateBackend'

    MAILCHIMP_API_KEY = 'yourapikey'

    # For the django back-end specifically
    TEMPLATED_EMAIL_MAILCHIMP = {
        'welcome':{
          'subject':'Welcome to my website',
          'track_opens':True,
          'track_clicks':False,
          'tags':['my','little','pony'],
        }
    }


.. _Django: http://djangoproject.com
