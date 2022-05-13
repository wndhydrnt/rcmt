Actions
=======

Actions encapsulate behavior of how to change a file.

Absent
------

.. autoclass:: rcmt.package.action.Absent

DeleteKey
---------

.. autoclass:: rcmt.package.action.DeleteKey


DeleteLineInFile
----------------

.. autoclass:: rcmt.package.action.DeleteLineInFile

Exec
----

.. autoclass:: rcmt.package.action.Exec

LineInFile
------------

.. autoclass:: rcmt.package.action.LineInFile

.. _action/Merge:

Merge
-----

.. autoclass:: rcmt.package.action.Merge

.. _action/Own:

Own
---

.. autoclass:: rcmt.package.action.Own

ReplaceInLine
-------------

.. autoclass:: rcmt.package.action.ReplaceInLine

Seed
----

.. autoclass:: rcmt.package.action.Seed

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

