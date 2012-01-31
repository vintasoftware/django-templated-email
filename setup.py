from setuptools import setup, find_packages
import os
import platform

DESCRIPTION = "A Django oriented templated / transaction email abstraction"

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.rst').read()
except:
    pass

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Framework :: Django',
]

setup(
    name='django-templated-email',
    version='0.4.1',
    packages=['templated_email','templated_email.backends'],
    author='Bradley Whittington',
    author_email='radbrad182@gmail.com',
    url='http://github.com/bradwhittington/django-templated-email/',
    license='MIT',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms=['any'],
    classifiers=CLASSIFIERS,
)

