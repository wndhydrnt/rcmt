rcmt
====

rcmt (short for Repository Configuration Management Tool) helps aligning configuration
files across many repositories. It creates, modifies or deletes files in multiple
repositories, then creates a Pull Request that contains the changes for each repository.

Quick start
-----------

Let's say you want to make flake8 `compatible with black <https://black.readthedocs.io/en/stable/guides/using_black_with_other_tools.html#flake8>`_.
To accomplish this, the file `.flake8` can be placed into every repository.

The content of `.flake8` looks like this:

.. highlight:: ini
.. include:: ./examples/simple/packages/flake8/.flake8
   :code:

Having to place this file in every repository, commit the change, create a pull request,
wait for a build job to succeed and then merge the pull request is no fun. This is where
rcmt can help.

First, you create a :doc:`Package <package>`. A package is a directory that contains the
file **manifest.yaml**. The manifest describes which :doc:`Actions <action>` to apply to
a repository. The directory can contain additional files that some actions need to work.

The basic directory structure of a package looks like this:

.. code-block:: bash

   .
   |____packages
   | |____flake8
   | | |____.flake8
   | | |____manifest.yaml

And the Manifest looks like this:

.. highlight:: yaml
.. include:: ./examples/simple/packages/flake8/manifest.yaml
   :code:

Packages describe what to do, but not to which repositories they apply. rcmt expects a
**matcher** to do this:

.. highlight:: yaml
.. include:: ./examples/simple/matcher.yaml
   :code:

Everything is ready. Run rcmt:

.. code-block:: bash

   rcmt run --packages ./packages ./matcher.yaml

rcmt will find all matching repositories, check them out locally, apply the package and
create a Pull Request for each repository.

.. toctree::
   :maxdepth: 1

   installation
   package
   action
   matcher
   sources
   configuration
   encoding
   customization
   faq
