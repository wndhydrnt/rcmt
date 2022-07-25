Sources
=======

A Source hosts git repositories. rcmt uses a Source to match Actions to repositories,
clones the repositories that match and applies Actions to their data. It creates a pull
request via the Source if an Action changes files.

rcmt supports the following Sources:

GitHub
------

- :ref:`Configuration <configuration/github>`

Gitlab
------

- :ref:`Configuration <configuration/gitlab>`

Base Classes
------------

.. autoclass:: rcmt.source.Base
   :members:

.. autoclass:: rcmt.source.Repository
   :members:
