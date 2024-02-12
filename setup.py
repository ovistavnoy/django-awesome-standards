import os
from setuptools import setup, find_packages

from standards import __version__


base_dir = os.path.dirname(__file__)
with open(os.path.join(base_dir, "README.rst")) as f:
    long_description = f.read()

setup(
    name='django-awesome-standards',
    version=__version__,
    description='Django awesome standards package',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author='Maxim Shaitanov',
    author_email='maximshaitanov@gmail.com',
    url='https://gitlab.com/kastielspb/django-awesome-standards.git',
    packages=find_packages(exclude=['example', 'tests']),
    include_package_data=True,
    license='MIT',
    install_requires=[
        'django>=2.1',
        'djangorestframework',
        'djangorestframework-camel-case>=1.1.2',
        'drf-orjson-renderer>=1.1.3',
    ],
    classifiers=[
        'Environment :: Web Environment',
        "Operating System :: OS Independent",
        "Framework :: Django",
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ]
)
