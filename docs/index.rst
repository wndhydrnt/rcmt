rcmt
====

rcmt (short for Repository Configuration Management Tool) helps aligning configuration
files across many repositories. It creates, modifies or deletes files in multiple
repositories, then creates a Pull Request that contains the changes for each repository.

Quick start
-----------

Let's say you want to make flake8 `compatible with black <https://black.readthedocs.io/en/stable/guides/using_black_with_other_tools.html#flake8>`_.
To accomplish this, the file `.flake8` can be placed into every repository.

The content of the file `.flake8` looks like this:

.. code-block:: ini

   [flake8]
   max-line-length = 88
   extend-ignore = E203

Having to place this file in every repository, commit the change, create a pull request,
wait for a build job to succeed and then merge the pull request is no fun. This is where
rcmt can help.

rcmt needs configuration that tells it what to do and to which repositories it should
apply changes. This is done via a **Task**. A Task is written in Python and stored in a
file typically named ``task.py``.

.. highlight:: python
.. include:: ./examples/simple/task.py
   :code:

Everything is ready. Run rcmt:

.. code-block:: bash

   rcmt run ./task.py

rcmt will find all matching repositories, check them out locally, apply the Action and
create a Pull Request for each repository.

.. toctree::
   :maxdepth: 1

   installation
   action
   task
   sources
   configuration
   encoding
   customization
   faq
