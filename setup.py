from setuptools import setup
from pip.req import parse_requirements
from datary.version import __version__

install_reqs = parse_requirements('requirements.txt', session=False)
required = [str(ir.req) for ir in install_reqs]

setup(
  name='datary',
  packages=['datary'],
  version=__version__,
  description='Datary Python sdk lib',
  author='Datary developers team',
  author_email='support@datary.io',
  url='https://github.com/Datary/python-sdk',
  download_url='https://github.com/Datary/python-sdk',
  keywords=['datary', 'sdk', 'api'],  # arbitrary keywords
  long_description=open("README.md").read(),
  classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
  install_requires=required,
)
