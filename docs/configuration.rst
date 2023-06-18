Configuration
=============

Example
-------

.. code-block:: yaml

   dry_run: true
   git:
     branch_name: rcmt-updates
   log_level: debug

Reference
---------

``database``
^^^^^^^^^^^^

``connection``
""""""""""""""

Connection to a database where rcmt stores additional data. The value is an
`SQLAlchemy Database URL <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_.
Defaults to ``sqlite:///:memory:``.

.. note::
   rcmt does not include database drivers like ``psycopg2`` or ``mysqlclient``. These
   packages need to be installed separately.

``migrate``
"""""""""""

Run migrations at the start of rcmt. Defaults to ``true``.

``dry_run``
^^^^^^^^^^^

Matches repositories, checks them out and applies actions but does not create pull
requests. Defaults to ``false``.

``git``
^^^^^^^

.. _configuration/branch_prefix:

``branch_prefix``
"""""""""""""""""

Prefix of git branches that rcmt creates. Not used if a Matcher defines its own
:ref:`branch_name <matcher/branch_name>`. Defaults to ``rcmt/``.

``clone_options``
"""""""""""""""""

Key/value pairs to pass as additional flags to ``git clone``.

See the `official docs <https://www.git-scm.com/docs/git-clone>`_ on ``git clone``
for all available flags.

Defaults to

.. code-block:: yaml

   filter: "blob:none"

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

Access token to authenticate at the GitHub API.

.. _configuration/gitlab:

``gitlab``
^^^^^^^^^^

``private_token``
"""""""""""""""""

Private token to authenticate at the GitLab API.

``url``
"""""""

URL of the GitLab installation. Defaults to ``https://gitlab.com``.

``json``
^^^^^^^^

Settings of the Json encoding.

``extensions``
""""""""""""""

List of file extensions that the JSON encoding supports. Defaults to ``[".json"]``.

``indent``
""""""""""

Indentation to use when writing JSON files. Defaults to ``2``.

``log_format``
^^^^^^^^^^^^^^

Format of log records. If not set, rcmt will auto-detect if it is run from a terminal
and pretty-print records. Otherwise it uses JSON.

Set to ``json`` to force JSON format.

Set to ``console`` to force pretty-printing of log records.

.. versionadded:: 0.20.0

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

Environment Variables
---------------------

rcmt can read settings from environment variables. A environment variable has to start
with ``RCMT_``. ``__`` separates sub-sections.

.. note::
   Values set in the configuration file take precedence over environment variables.

Examples
^^^^^^^^

.. code-block:: shell

   export RCMT_DRY_RUN=true
   export RCMT_LOG_LEVEL=warn
   export RCMT_GITHUB__ACCESS_TOKEN=token
