
import codecs
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os
import re

version = '1.1.'
try:
    circle_build_num = os.environ['CIRCLE_BUILD_NUM']
    version += circle_build_num
except KeyError:
    print("Couldn't find CIRCLE_BUILD_NUM, using 0 as minor instead")
    version += '0'

def read(*parts):
    return codecs.open(os.path.join(os.path.dirname(__file__), *parts),
                       encoding='utf8').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='django-revproxy',
    description='Yet another Django reverse proxy application.',
    version=find_version('revproxy/__init__.py'),
    long_description=read('README.rst'),
    packages=['revproxy'],
    install_requires=[
        'django==1.9.13',
        'urllib3==1.25.6',
        'zipp==1.2.0',
    ],
    extras_require={
        'diazo': ['diazo>=1.0.5', 'lxml>=3.4'],
    },
    tests_require=['mock', 'diazo', 'lxml>=3.4', 'zipp==1.2.0'],
    test_suite="tests.run.runtests",
    author='Sergio Oliveira',
    author_email='sergio@tracy.com.br',
    url='https://github.com/TracyWebTech/django-revproxy',
    license='MPL v2.0',
    include_package_data=True,
    zip_safe=False,
    keywords='django-revproxy',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: Proxy Servers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        ],
)
