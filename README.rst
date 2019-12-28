Franklin Citation Toolkit
=========================

.. image:: https://readthedocs.org/projects/franklin/badge/?version=latest
  :target: https://franklin.readthedocs.io/en/latest/?badge=latest
     :alt: Documentation Status
.. image:: https://travis-ci.com/canismarko/franklin.svg?branch=master
  :target: https://travis-ci.com/canismarko/franklin
.. image:: https://coveralls.io/repos/github/canismarko/franklin/badge.svg?branch=master
  :target: https://coveralls.io/github/canismarko/franklin?branch=master
.. image:: https://badge.fury.io/py/franklin.svg
  :target: https://badge.fury.io/py/franklin	   

``franklin`` is a set of tools for accessing research articles and
their associated bibtex references.

The following console scripts are available.

- ``fetch-doi`` - Retrieve PDFs and bibtex entries.
- ``abbreviate-journals`` - Parse a bibtex file and look up abbreviated journal names.
- ``bibtex-cleanup`` - [coming soon] Parse a bibtex file and clean it up.

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

Development
-----------
	   
For development, a **developer installation** through pip is recommended.

.. code:: bash
	  
	  $ git fetch https://github.com/canismarko/franklin.git
	  $ pip install franklin/requirements.txt
	  $ pip install -e franklin/

Run the tests using pytest:

.. code:: bash

	  $ pytest
