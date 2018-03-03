from setuptools import setup, find_packages

import etcd3wrapper as pkg

readme = open('README.rst').read()
history = open('HISTORY.rst').read()
reqs = [x.strip() for x in open('requirements.txt').readlines()]
test_reqs = [x.strip() for x in open('requirements-tests.txt').readlines()]

setup(
    name=pkg.__name__,
    version=pkg.__version__,
    author=pkg.__author__,
    author_email=pkg.__email__,
    packages=find_packages(include=(pkg.__name__, pkg.__name__ + '.*',)),
    description='Python 3 etcd3 wrapper for protobuf',
    keywords='',
    include_package_data=True,
    long_description=readme,
    install_requires=reqs,
    test_suite='tests',
    tests_require=test_reqs,
)
