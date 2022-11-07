.. Parseed documentation master file, created by
   sphinx-quickstart on Wed Sep 21 21:05:58 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Parseed's documentation!
===================================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   how_to_use
   language
   generators/make_a_generator
   internal/modules


Parseed is a project made of a language and a transpiler that enables you to easily create parsers in any language.

The language is inspired by the C language, it is composed of structures and bitfields.


How to use Parseed ?
====================

The transpiler is written in Python 3 and uses typing annotations, so you will need Python 3.5 or greater.

The transpiler can be used in the command line.

Here is an example:

.. code-block:: bash

   ./parseed.py -G python_class example/arp.py


The language
============

You can find a tutorial of the language on this page: :doc:`language`.


Making your own generator
-------------------------

If you are interested in making your own generator, you can find how to do it in here: :doc:`generators/make_a_generator`.


Parseed's internals documentation
---------------------------------

If you are intersted in hacking Parseed, here is the API documentation: :doc:`internal/modules`


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`