Package
=======

A Package is a directory that  contains the instructions and files needed to put a
repository into the desired state.

Manifest
--------

.. autoclass:: rcmt.package.manifest.Manifest
   :members:

The Manifest describes the :doc:`Actions <action>` that rcmt applies to each repository.
Every Package contains at least a Manifest file. The name of the Manifest file is
``manifest.py``.

Example
^^^^^^^

Take a look at the `package example <https://github.com/wndhydrnt/rcmt/tree/main/docs/examples/package>`_
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
