Matcher
=======

A Matcher connects packages with repositories. rcmt reads the Matcher, finds
repositories and then applies packages to each repository.

Example
-------

.. code-block:: yaml

   match:
     repository: ^github.com/wndhydrnt/rcmt$
   name: python-defaults
   packages: ["flake8"]

``match``
---------

``repository``
^^^^^^^^^^^^^^

The repositories to match. rcmt compiles the string into a regular expression.

``name``
--------

The name of the matcher.

``packages``
------------

A list of :doc:`Packages<package>`. rcmt applies each package to each matching
repository.
