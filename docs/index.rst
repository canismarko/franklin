.. Franklin documentation master file, created by
   sphinx-quickstart on Fri Apr 19 13:41:16 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Franklin's documentation!
====================================

``franklin`` is a set of tools for accessing research articles and
their associated bibtex references.

The following console scripts are available.

- ``fetch-doi`` - Retrieve PDFs and bibtex entries.
- ``bibtex-cleanup`` - [coming soon] Parse a bibtex file and clean it up.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   publishers

Installation
============

The easiest way to install franklin is **through the Python package
index**.

.. code:: bash

	  $ pip install franklin

For development, a **developer installation** through pip is recommended.

.. code:: bash
	  
	  $ git fetch https://github.com/canismarko/franklin.git
	  $ pip install franklin/requirements.txt
	  $ pip install -e franklin/

Command-Line Scripts
====================

Fetch DOI
---------

The fetch DOI script will retrieve the bibtex entry and, if possible,
the PDF of an article.

Retrieving the PDF requires either an open-access article or
institutional access (eg. through VPN). The following publishers are
currently supported:

- American Chemical Society (ACS)
- The Electrochemical Society (ECS)
- Elsevier
- Springer

To request support for additional publishers, please `submit an
issue`_. If possible, include the DOI of an open-access article for
testing.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`

.. _submit an issue: https://github.com/canismarko/franklin/issues
