Class Reference
===============

This reference describes the internal APIs of SpenDB. Note that these APIs 
should not be considered stable and that they may change between releases. If you
want to develop an application or extension to use SpenDB, you should try
to use web-based interfaces as much as possible. If some functionality is not 
available remotely, it may be worth implementing an additional interface rather 
than relying on the core to remain stable.


Dataset: metadata and core functions
------------------------------------

.. automodule:: spendb.model.dataset

  .. autoclass:: Dataset
     :members:

Attributes, Dimensions and Measures
-----------------------------------

.. automodule:: spendb.model.attribute

  .. autoclass:: Attribute
     :members:

.. automodule:: spendb.model.dimension

  .. autoclass:: Measure
     :members:

  .. autoclass:: Dimension
     :members:

  .. autoclass:: AttributeDimension
     :members:
  
  .. autoclass:: CompoundDimension
     :members:
  
  .. autoclass:: DateDimension
     :members:



