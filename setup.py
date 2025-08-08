import os
import sys
from setuptools import setup, find_packages

DESCRIPTION = "A Django oriented templated / transaction email abstraction"
VERSION = '3.1.0'
LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.rst').read()
except:
    pass

requirements = [
    'django-render-block>=0.5'
]

# python setup.py publish
if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    sys.exit()

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: 3.13',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Framework :: Django',
]

setup(
    name='django-templated-email',
    version=VERSION,
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,
    author='Bradley Whittington',
    author_email='radbrad182@gmail.com',
    url='http://github.com/vintasoftware/django-templated-email/',
    license='MIT',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    platforms=['any'],
    classifiers=CLASSIFIERS,
    install_requires=requirements,
)
