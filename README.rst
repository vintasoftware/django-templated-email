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

Getting going - installation
=============

Installing::

    pip install templated_email

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

    from templated_email import send_templated_email
    send_templated_email(
            template_name='welcome',
            from_email='from@example.com',
            recipient_list=['to@example.com'],
            context={
                'username':request.user.username,
                'full_name':request.user.get_full_name(),
                'signup_date':request.user.date_joined
            }
    )

Which looks in django template directories/loaders for  
*templated_email/welcome.txt* ::

    Hey {{full_name}},

    You just signed up for my website, using:
        username: {{username}}
        join date: {{signup_date}}

    Thanks, you rock!

It will also use *templated_email/welcome.html* for the html part 
of the email allowing you to make it so much pretty. It is plausible
that one day there will be support for attachments and inline mime / images

.. _Django: http://djangoproject.com
