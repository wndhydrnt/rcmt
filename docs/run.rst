Run
===

A Run connects Actions with repositories. rcmt reads the Run, finds
repositories and then applies Actions to each repository.

.. autoclass:: rcmt.run.Run
   :members:

Matchers
--------

A Run uses Matchers to find the repositories to which it applies Actions.

And
^^^

.. autoclass:: rcmt.matcher.And

FileExists
^^^^^^^^^^

.. autoclass:: rcmt.matcher.FileExists

FileNotExists
^^^^^^^^^^^^^

.. autoclass:: rcmt.matcher.FileNotExists

LineInFile
^^^^^^^^^^

.. autoclass:: rcmt.matcher.LineInFile

LineNotInFile
^^^^^^^^^^^^^

.. autoclass:: rcmt.matcher.LineNotInFile

Not
^^^

.. autoclass:: rcmt.matcher.Not

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
