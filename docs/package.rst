Package
=======

A Package is a directory that  contains the instructions and files needed to put a
repository into the desired state.

Manifest
--------

The Manifest describes the :doc:`Actions <action>` that rcmt applies to each repository.
Every Package contains at least a Manifest file. The name of the Manifest file is
``manifest.yaml``.

Example
^^^^^^^

Take a look at the `simple example <https://github.com/wndhydrnt/rcmt/tree/main/docs/examples/simple>`_
at GitHub.

Reference
^^^^^^^^^

``actions``
"""""""""""

A list of :doc:`Actions <action>`.

``name``
""""""""

The name of the package. Two packages cannot share the same name.

Supporting Files
----------------

Some Actions, like :ref:`Merge <action/Merge>` or :ref:`Own <action/Own>`, require files
they use as a blueprint. Those files can be placed next to the Manifest file.

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
