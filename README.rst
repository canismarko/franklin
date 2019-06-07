Franklin Citation Toolkit
=========================

.. image:: https://readthedocs.org/projects/franklin/badge/?version=latest
  :target: https://franklin.readthedocs.io/en/latest/?badge=latest
     :alt: Documentation Status
.. image:: https://travis-ci.com/canismarko/franklin.svg?branch=master
  :target: https://travis-ci.com/canismarko/franklin
.. image:: https://coveralls.io/repos/github/canismarko/franklin/badge.svg?branch=master
  :target: https://coveralls.io/github/canismarko/franklin?branch=master

``franklin`` is a set of tools for accessing research articles and
their associated bibtex references.

The following console scripts are available.

- ``fetch-doi`` - Retrieve PDFs and bibtex entries.
- ``bibtex-cleanup`` - [coming soon] Parse a bibtex file and clean it up.
	   
For development, a **developer installation** through pip is recommended.

.. code:: bash
	  
	  $ git fetch https://github.com/canismarko/franklin.git
	  $ pip install franklin/requirements.txt
	  $ pip install -e franklin/

Run the tests using pytest:

.. code:: bash

	  $ pytest
