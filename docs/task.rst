Task
====

A Task connects Actions with repositories. rcmt reads the Task, finds
repositories and then applies Actions to each repository.

.. autoclass:: rcmt.task.Task
   :members:

Matchers
--------

A Task uses Matchers to find the repositories to which it applies Actions.

And
^^^

.. autoclass:: rcmt.matcher.And

FileExists
^^^^^^^^^^

.. autoclass:: rcmt.matcher.FileExists

LineInFile
^^^^^^^^^^

.. autoclass:: rcmt.matcher.LineInFile

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
