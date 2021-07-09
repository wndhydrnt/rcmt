"""
rcmt
####

rcmt (short for Repository Configuration Management Tool) helps aligning configuration
files across many repositories.


Installation
************

.. code-block:: bash

   pip install rcmt
   rcmt --help


Quickstart
**********

Let's say you want to configure flake8 to be `compatible with black <https://black.readthedocs.io/en/stable/guides/using_black_with_other_tools.html#flake8>`_.
To accomplish this, the file `.flake8` can be placed into every repository.

The content of `.flake8` looks like this:

.. highlight:: ini
.. include:: ./examples/simple/packages/flake8/.flake8
   :code:

Having to place a file in every repository, commit the change, create a pull request,
wait for a build job to succeed and then merge is no fun. This is where rcmt can help.

First, you create a **package**. A package is a directory that contains the files you
want to look the same across different repositories plus a file called **manifest.yaml**
that tells rcmt how to handle each file.

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

   ./bin/rcmt run --packages ./docs/examples/simple/packages ./docs/examples/simple/matcher.yaml

"""
import importlib.metadata

from .rcmt import options_from_config, run

try:
    __version__ = importlib.metadata.version(__name__)
except:
    __version__ = "develop"
