from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
from pkg_resources import DistributionNotFound

import sys
import os

if sys.version_info < (2, 4):
    raise SystemExit("Python 2.4 or later is required")

execfile(os.path.join("dawpag", "release.py"))

# setup params
install_requires = [
    "ConfigObj >= 4.3.2",
    "setuptools >= 0.6c2",
    "SQLAlchemy >= 0.5.0alpha"
]

if sys.version_info < (2, 5):
    install_requires.extend([
            # Py < 2.5 does not include SQLite
            "pysqlite",
        ])


setup(
    name="DawPaG",
    version=version,
    author=author,
    author_email=email,
    download_url="http://www.exatisistemas.com.br/dawpag/download",
    dependency_links=[
        "http://www.exatisistemas.com.br/dawpag/eggs",
        ],
    license=license,
    description="Rapid Desktop Development With Python and GTK",
    long_description="""\
Rapid Desktop Development With Python and GTK
=============================================

Dawpag combines the power and portability of Python and GTK to create an
easy to install, easy to use framework, a little based on MVC model
""",
    url="http://www.exatisistemas.com.br/dawpag",
    zip_safe=False,
    install_requires = install_requires,
    packages=find_packages(),
    include_package_data=True,
    # create = dawpag.command.create:create
    # sql = dawpag.command.base:SQL
    entry_points = """
    [console_scripts]
    dpadmin = dawpag.command:main

    [dawpag.command]
    console = dawpag.command.base:Console

    """#,

    # classifiers = [
    #     'Development Status :: 5 - Production/Stable',
    #     'Environment :: Console',
    #     'Intended Audience :: Developers',
    #     'License :: OSI Approved :: MIT License',
    #     'Operating System :: OS Independent',
    #     'Programming Language :: Python',
    #     'Topic :: Software Development :: Libraries :: Python Modules'],
    # test_suite = 'nose.collector',
)