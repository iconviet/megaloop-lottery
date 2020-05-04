# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# All dependences
deps = {
    'test': [],
    'dev': ['iconsdk', 'tbears', 'pylint', 'autopep8', 'rope', 'black',],
}

install_requires = []
extra_requires = deps
test_requires = deps['test']

with open('README.adoc') as readme_file:
    long_description = readme_file.read()

setup(
    name='icon_lottery',
    version='0.0.1',
    description='A probabilistic lottery Dapp on ICON network',
    long_description=long_description,
    long_description_content_type='text/asciidoc',
    author='duyyudus',
    author_email='duyyudus@gmail.com',
    url='https://github.com/duyyudus/icon-lottery',
    include_package_data=True,
    tests_require=test_requires,
    install_requires=install_requires,
    extras_require=extra_requires,
    license='MIT',
    zip_safe=False,
    keywords='Lottery Dapp',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
    ],
)
