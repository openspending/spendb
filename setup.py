import os
from setuptools import setup, find_packages


PKG_ROOT = os.path.abspath(os.__file__)


def files_in_pkgdir(pkg, dirname):
    pkgdir = os.path.join(PKG_ROOT, *pkg.split('.'))
    walkdir = os.path.join(pkgdir, dirname)
    walkfiles = []
    for dirpath, _, files in os.walk(walkdir):
        fpaths = (os.path.relpath(os.path.join(dirpath, f), pkgdir)
                  for f in files)
        walkfiles += fpaths
    return walkfiles

try:
    import spendb
    release = spendb.__version__
except:
    release = 'dev'


def package_filter(pkg):
    """
    Filter packages so that we exclude test cases but include regular test
    objects available in spendb.tests' modules (all test cases are
    in subdirectories).
    """

    # We want to include spendb.tests but not its subpackages
    # Hence we only check for things starting with spendb.tests.
    # (note the trailing period to denote subpackages)
    return not pkg.startswith('spendb.tests.')

setup(
    name='spendb',
    version=release,
    description='SpenDB',
    author='Friedrich Lindenberg (formerly OKFN)',
    author_email='friedrich@pudo.org',
    url='http://github.com/pudo/spendb',
    install_requires=[],
    setup_requires=[],
    packages=filter(package_filter, find_packages()),
    namespace_packages=['spendb'],
    package_data={
        'spendb': (
            files_in_pkgdir('spendb', 'static') +
            files_in_pkgdir('spendb', 'templates') +
            files_in_pkgdir('spendb', 'reference/data')
        )
    },
    test_suite='nose.collector',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'spendb = spendb.command:main'
        ],
        'cubes.providers': [
            'spending = spendb.model.provider:SpendingModelProvider'
        ],
        'cubes.stores': [
            'spending = spendb.model.provider:SpendingStore'
        ]
    },
    message_extractors={
        'spendb': [('**.py', 'python', None),
                   ('templates/**.html', 'jinja2', None),
                   ('static/**', 'ignore', None),
                   ]
    },
)
