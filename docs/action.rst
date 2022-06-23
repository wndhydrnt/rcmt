Actions
=======

Actions encapsulate behavior of how to change a file.

Absent
------

.. autoclass:: rcmt.action.Absent

DeleteKey
---------

.. autoclass:: rcmt.action.DeleteKey


DeleteLineInFile
----------------

.. autoclass:: rcmt.action.DeleteLineInFile

Exec
----

.. autoclass:: rcmt.action.Exec

LineInFile
------------

.. autoclass:: rcmt.action.LineInFile

.. _action/Merge:

Merge
-----

.. autoclass:: rcmt.action.Merge

.. _action/Own:

Own
---

.. autoclass:: rcmt.action.Own

ReplaceInLine
-------------

.. autoclass:: rcmt.action.ReplaceInLine

Seed
----

.. autoclass:: rcmt.action.Seed

Templating
----------

Some Actions support templating.

rcmt renders a `Template string <https://docs.python.org/3/library/string.html#template-strings>`_
and passes the following variables to it:

- ``$repo_name`` - The name of the repository, e.g. ``rcmt``.
- ``$repo_project`` - The name of the owner, org or project, e.g. ``wndhydrnt``.
- ``$repo_source`` - The address of the source that hosts the repository, e.g.
  ``github.com``.

Take a look at the `templating example <https://github.com/wndhydrnt/rcmt/blob/main/docs/examples/templating>`_
for how to use these variables.

