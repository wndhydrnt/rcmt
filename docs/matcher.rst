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

Every :doc:`Source <sources>` has its own way of creating this string:

====== =============================================== =============================
Source Schema                                          Example
====== =============================================== =============================
GitHub ``github.com/<owner or org>/<repository name>`` ``github.com/wndhydrnt/rcmt``
====== =============================================== =============================

``name``
--------

The name of the matcher.

``packages``
------------

A list of :doc:`Packages<package>`. rcmt applies each package to each matching
repository.
