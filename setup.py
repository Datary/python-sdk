from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
  name='datary',
  packages=['datary'],
  version='0.1',
  description='Datary Python sdk lib',
  author='Datary developers team',
  author_email='support@datary.io',
  url='https://github.com/Datary/python-sdk',
  download_url='https://github.com/Datary/python-sdk',
  keywords=['datary', 'sdk', 'api'],  # arbitrary keywords
  classifiers=['Programming Language :: Python :: 3.4'],
  install_requires=required,
)
