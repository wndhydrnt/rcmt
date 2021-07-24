Actions
=======

Actions encapsulate behavior of how to change a file.

Absent
------

Deletes a file or directory.

Parameters
^^^^^^^^^^

====== ======================================== ======== =======
Name   Description                              Required Default
====== ======================================== ======== =======
target Path to the file or directory to delete. yes      /
====== ======================================== ======== =======

Examples
^^^^^^^^

.. code-block:: yaml

   - absent:
       target: config.yaml

DeleteKey
---------

Delete a key in a file. The file has to be in a format supported by :doc:`encoding`.

Parameters
^^^^^^^^^^

====== ======================================== ======== =======
Name   Description                              Required Default
====== ======================================== ======== =======
key    Path to the key in the data structure.   yes      /
target Path to the file to modify.              yes      /
====== ======================================== ======== =======

Examples
^^^^^^^^

.. code-block:: yaml

   # Delete key "bar" in dict "foo".
   - delete_key:
       key: "foo.bar"
       target: config.json

Exec
----

Exec calls an executable and passes matching files in a repository to it. The executable
can then modify each file.

The executable should expect the path of a file as its only positional argument.

Parameters
^^^^^^^^^^

======== ============================================== ======== =======
Name     Description                                    Required Default
======== ============================================== ======== =======
path     Path to the executable.                        yes      /
selector Glob selector to find the files to modify.     yes      /
timeout  Maximum runtime of the executable, in seconds. no       120
======== ============================================== ======== =======

Examples
^^^^^^^^

.. code-block:: yaml

   # Find all Python files in a repository recursively and pass each path to /opt/the-binary.
   - exec:
       path: /opt/the-binary
       selector: "**/*.py"

Merge
-----

Merge merges the content of a file in a repository with the content of a file from a
package.

It supports merging of various file formats through :doc:`encoding`.

Parameters
^^^^^^^^^^

========= ============================================================= ======== =======
Name      Description                                                   Required Default
========= ============================================================= ======== =======
selector  Glob selector to find the files to merge.                     yes      /
source    Path to the file that contains the source data.               yes      /
strategy  | Strategy to use when merging data. ``replace`` replaces a   no       replace
          | key if it already exists. ``additive`` combines
          | collections, e.g. ``list`` or ``set``.
========= ============================================================= ======== =======

Examples
^^^^^^^^

.. code-block:: yaml

   # Ensure that pyproject.toml contains specific keys.
   - merge:
       selector: pyproject.toml
       source: pyproject.toml

Own
---

Own ensures that a file in a repository stays the same.

It always overwrites the data in the file with the data from a package.

Parameters
^^^^^^^^^^

====== ============================================================== ======== =======
Name   Description                                                    Required Default
====== ============================================================== ======== =======
source Path to the file in the package that contains the source data. yes      /
target Path to the file in a repository to own.                       yes      /
====== ============================================================== ======== =======

Examples
^^^^^^^^

.. code-block:: yaml

   # Ensure that .flake8 looks the same across all repositories.
   - own:
       source: .flake8
       target: .flake8

Seed
----

Seed ensures that a file in a repository is present.

It does not modify the file again if the file is present in a repository.

Parameters
^^^^^^^^^^

====== ============================================================== ======== =======
Name   Description                                                    Required Default
====== ============================================================== ======== =======
source Path to the file in the package that contains the source data. yes      /
target Path to the file in a repository to seed.                      yes      /
====== ============================================================== ======== =======

Examples
^^^^^^^^

.. code-block:: yaml

   # Ensure that the default Makefile is present.
   - seed:
       source: Makefile
       target: Makefile
