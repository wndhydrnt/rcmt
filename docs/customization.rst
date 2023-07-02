Extending rcmt
==============

It is possible to extend rcmt add custom Matchers, Actions or Sources.

Add a custom Action to a Task
-----------------------------

.. highlight:: python
.. include:: ./examples/writing_an_action/task.py
   :code:

Write a custom Action using ``GlobMixin``
-----------------------------------------

.. highlight:: python
.. include:: ./examples/customization/custom_action_globmixin.py
   :code:

Add a custom Matcher to a Task
------------------------------

.. highlight:: python
.. include:: ./examples/writing_a_matcher/task.py
   :code:

Add a custom Source
-------------------

.. highlight:: python
.. include:: ./examples/customization/custom_source.py
   :code:
