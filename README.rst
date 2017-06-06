Datary SDK for Python
======================

.. image:: https://img.shields.io/pypi/v/datary.svg
   :target: https://pypi.python.org/pypi/datary
   :alt: downloads


Install Dependencies
----------------------

.. code-block:: console

    $ pip install datary

Generate docs
---------------
Documentation powered by sphinx.

.. code-block:: console
    
    $ cd docs && make docs OUTPUT_FORMAT

Usage
--------
Example to retrieve Datary repository info

.. code-block:: pycon

  from datary import Datary

  # init Datary class using username&password or token
  d = Datary(username='test_user', password='test_password')
  # d = Datary(token='test_token')

  # return repo description asociated to the name introduced and to the account.
  repo = d.get_describerepo(repo_name='test_repo_name')
