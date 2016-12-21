from setuptools import setup
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session=False)
required = [str(ir.req) for ir in install_reqs]

setup(
  name='datary',
  packages=['datary'],
  version='0.0.1',
  description='Datary Python sdk lib',
  author='Datary developers team',
  author_email='support@datary.io',
  url='https://github.com/Datary/python-sdk',
  download_url='https://github.com/Datary/python-sdk',
  keywords=['datary', 'sdk', 'api'],  # arbitrary keywords
  classifiers=['Programming Language :: Python :: 3.4'],
  install_requires=required,
)
