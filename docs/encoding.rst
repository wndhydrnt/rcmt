Encodings
=========

Some Actions, like the :ref:`Merge action <action/Merge>`, need to decode a file written
in a format, modify data and then encode the data again before writing it back to the
file.

Encodings abstract the decoding and encoding part, allowing actions to support many file
formats without having to implement each format separately.

Bundled Encodings
^^^^^^^^^^^^^^^^^

.. autoclass:: rcmt.encoding.Json

.. autoclass:: rcmt.encoding.Toml

.. autoclass:: rcmt.encoding.Yaml

Base Class
^^^^^^^^^^

.. autoclass:: rcmt.encoding.Encoding
   :members:
