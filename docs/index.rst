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
- ``abbreviate-journals`` - Parse a bibtex file and abbreviate the journal titles.
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
institutional access (e.g. through VPN). The following publishers are
currently supported:

- American Chemical Society (ACS)
- The Electrochemical Society (ECS)
- Elsevier
- Springer
- The Royal Society of Chemistry (RSC)

To request support for additional publishers, please `submit an
issue`_. If possible, include the DOI of an open-access article for
testing.

Abbreviate Journals
-------------------

The ``abbreviate-journals`` command line tool can be used to look up
abbreviated journal names from several sources.

First, a **dictionary of local journal abbreviations** is queried. This
can be skipped using the ``--no-native`` option.

Second, the **chemical abstract services source index** is
queried. Since CASSI does not provide an API, this involves directly
parsing HTML pages and so is not perfectly reliable. This option is
provided in good faith to comply with the usage guidelines set forth
by CASSI, since the retrieved data are not saved in a directory and
are retrieved one at a time. Please review the CASSI usage guidelines
and refrain from using this option if you do not agree to these
guidelines. This behavior can be disable by providing the
``--no-cassi`` option.

As a last resort, *franklin* will attempt to determine the journal
abbreviation directly the the ISSN list of title word abbreviations
(LTWA). This will always produce a result, but is currently very slow
and not well tested. This option can be disabled with the
``--no-ltwa`` option.

If the generated bibtex file will be used in an existing LaTeX
document, it may make sense to **limit the bibtex entries to only
those cited in the document.** This can be done using the
``--latex-aux-file`` (``-L``) argument and providing one or more
``.aux`` files generated from a ``.tex`` document..


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`

.. _submit an issue: https://github.com/canismarko/franklin/issues
