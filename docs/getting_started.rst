Getting started with Datary Python SDK lib
==========================================

Introduction
------------
This section will show good practices and a guide to actions that can be done with this Datary lib SDK

Init Datary
------------

Init using username & password
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python
   :linenos:

   from datary import Datary
   d = Datary(username='test_user', password='test_password')

Init using user token
~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python
   :linenos:

   from datary import Datary
   d = Datary(token='test_token')


Repository Methods
------------------

Create repo
~~~~~~~~~~~
.. code-block:: python
   :linenos:

   from datary import Datary
   d = Datary(username='test_user', password='test_password')
   d.create_repo(repo_name='repo_test',
                 repo_category='datary_repo_category',  # other as default
                 description='repo description test',   # repo_name description as default
                 visibility='datary_visibility_option', # commercial as default
                 license='license_test'                 # propietary as default
                )