Configuration
=============

Example
-------

.. code-block:: yaml

   auto_merge: true
   dry_run: true
   git:
     branch_name: rcmt-updates
   log_level: debug

Reference
---------

``auto_merge``
^^^^^^^^^^^^^^

rcmt automatically merges a pull request on its next run. The pull request must pass all
its checks. Defaults to ``false``.

``dry_run``
^^^^^^^^^^^

Matches repositories, checks them out and applies packages but does not create pull
requests. Defaults to ``false``.

``git``
^^^^^^^

``branch_name``
"""""""""""""""

Name of the branch to which rcmt adds its changes. Defaults to ``rcmt``.

``data_dir``
""""""""""""

Path to a directory where rcmt stores its temporary data, like checkouts of
repositories. Defaults to ``/tmp/rcmt/data``.

``user_email``
""""""""""""""

E-mail to set when committing changes. Defaults to ``""``.

``user_name``
"""""""""""""

Name of the author to set when committing changes. Defaults to ``rcmt``.

.. _configuration/github:

``github``
^^^^^^^^^^

``access_token``
""""""""""""""""

Access to authenticate at the GitHub API. It is also possible to set the access token
via the environment variable ``RCMT_GITHUB_ACCESS_TOKEN``.

``json``
^^^^^^^^

Settings of the Json encoding.

``extensions``
""""""""""""""

List of file extensions that the JSON encoding supports. Defaults to ``[".json"]``.

``indent``
""""""""""

Indentation to use when writing JSON files. Defaults to ``2``.

``log_level``
^^^^^^^^^^^^^

Log level of the application. Defaults to ``info``.

.. _configuration/pr_title_prefix:

``pr_title_prefix``
^^^^^^^^^^^^^^^^^^^

rcmt prefixes every Pull Request title with this string. Defaults to ``rcmt:``.

.. _configuration/pr_title_body:

``pr_title_body``
^^^^^^^^^^^^^^^^^

rcmt uses this string to set the title of each Pull Request. Defaults to
``apply matcher {matcher_name}``.

``matcher_name`` is a variable referencing the name of a :doc:`Matcher <matcher>`. No
other variables are supported.

.. _configuration/pr_title_suffix:

``pr_title_suffix``
^^^^^^^^^^^^^^^^^^^

rcmt suffixes every Pull Request title with this string. Defaults to ``""``.

``toml``
^^^^^^^^

Settings of the TOML encoding.

``extensions``
""""""""""""""

List of file extensions that the TOML encoding supports. Defaults to ``[".toml"]``.

``yaml``
^^^^^^^^

Settings of the YAML encoding.

``explicit_start``
""""""""""""""""""

Add an ``---`` at the beginning of a document. Defaults to ``false``.

``extensions``
""""""""""""""

List of file extensions that the YAML encoding supports. Defaults to
``[".yaml", ".yml"]``.
