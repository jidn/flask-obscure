"""
Flask-Obscure
-------------

This is the description for that library
"""
import os
import sys
from setuptools import setup

BASEDIR = os.path.dirname(__file__)

for _ in open(os.path.join(BASEDIR, 'flask_obscure.py')).readlines():
    if _.startswith('__version__'):
        exec(_.strip(), None)
        break

requirements = [
    'Flask>=0.10',
    'obscure'
]

setup(
    name='Flask-Obscure',
    url='http://www.github.com/jidn/flask-obscure/',
    author='Clinton James',
    author_email='clinton.james@anuit.com',
    description='Obscure numerical IDs in URLs',
    long_description=open(os.path.join(BASEDIR, 'README.rst')).read(),
    version='1.0',
    license='Apache License 2.0',
    keywords=['flask', 'REST', 'obfuscate', 'ID'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    py_modules=['flask_obscure'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=requirements,
)
