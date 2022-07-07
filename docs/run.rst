Run
===

A Run connects packages with repositories. rcmt reads the Run, finds
repositories and then applies packages to each repository.

.. autoclass:: rcmt.run.Run
   :members:

Matchers
--------

A Run uses Matchers to find the repositories to which it applies Packages.

FileExists
^^^^^^^^^^

.. autoclass:: rcmt.matcher.FileExists


LineInFile
^^^^^^^^^^

.. autoclass:: rcmt.matcher.LineInFile

Or
^^

.. autoclass:: rcmt.matcher.Or

RepoName
^^^^^^^^

.. autoclass:: rcmt.matcher.RepoName

Base Class
^^^^^^^^^^

.. autoclass:: rcmt.matcher.Base
   :members:
