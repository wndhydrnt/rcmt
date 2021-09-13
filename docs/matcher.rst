Matcher
=======

A Matcher connects packages with repositories. rcmt reads the Matcher, finds
repositories and then applies packages to each repository.

Example
-------

.. code-block:: yaml

   auto_merge_after: P7D
   match:
     files:
       - pyproject.toml
     repository: ^github.com/wndhydrnt/rcmt$
   name: python-defaults
   packages: ["flake8"]
   pr_title: A custom PR title
   pr_body: |
     A custom PR title.
     It supports multiline strings.


.. _matcher/auto_merge:

``auto_merge``
--------------

rcmt automatically merges a pull request on its next run. The pull request must pass all
its checks. Defaults to ``false``.


``auto_merge_after``
--------------------

A duration after which to automatically merge a Pull Request. Requires
:ref:`auto_merge <matcher/auto_merge>` to be set to ``true``.

The duration is given in `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601#Durations>`_
format.

.. _matcher/branch_name:

``branch_name``
---------------

Name of the branch in git. Defaults to :ref:`branch_prefix <configuration/branch_prefix>` +
:ref:`name <matcher/name>`.

``match``
---------

``files``
^^^^^^^^^

A list of files or directories that need to exist inside a repository for it to match.

rcmt queries a :doc:`Source <sources>` via its API instead of checking out the whole
repository.

``repository``
^^^^^^^^^^^^^^

The repositories to match. rcmt compiles the string into a regular expression.

Every :doc:`Source <sources>` has its own way of creating this string:

====== =============================================== =============================
Source Schema                                          Example
====== =============================================== =============================
GitHub ``github.com/<owner or org>/<repository name>`` ``github.com/wndhydrnt/rcmt``
GitLab ``<address>/<owner>/<project>``                 ``gitlab.com/wndhydrnt/rcmt``
====== =============================================== =============================

.. _matcher/name:

``name``
--------

The name of the matcher.

``packages``
------------

A list of :doc:`Packages<package>`. rcmt applies each package to each matching
repository.

``pr_body``
-----------

Define a custom body of a pull request.

``pr_title``
------------

Set a custom title for a pull request. Overrides :ref:`pr_title_prefix <configuration/pr_title_prefix>`,
:ref:`pr_title_body <configuration/pr_title_body>` and :ref:`pr_title_suffix <configuration/pr_title_suffix>`.
