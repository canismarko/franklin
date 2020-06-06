# This file is part of Franklin.
# 
# Franklin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Franklin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Franklin.  If not, see <https://www.gnu.org/licenses/>.

import os
import argparse
import re
import logging
from typing import List, Iterable

import bibtexparser

from .article import Article
from . import exceptions

log = logging.getLogger(__name__)


def parse_doi(doi):
    """Validate and extract a digital object identifier."""
    regex = ('(https?://)?((dx\.)?doi.org/)?'
             '([0-9.]+/[-a-zA-Z0-9._;()/#+<>]+)')
    match = re.match(regex, doi)
    if match:
        new_doi = match.group(4)
        logging.debug("Parsed DOI '%s' to '%s'.", doi, new_doi)
    else:
        raise exceptions.DOIError("Malformed DOI: '%s'" % doi)
    return new_doi


def existing_ids(doi: str, bib_entries: Iterable) -> List:
    """Look through a bibtex bibliography and check for duplicate entry.
    
    Parameters
    ==========
    doi
      The digital object identifier to search for.
    bib_entries
      The bibliography data to look in.
    
    Returns
    =======
    existing_ids : 
      List of the IDs of existing entries with this same DOI.
    
    """
    existing_ids = [e.get('ID') for e in bib_entries if e.get('doi', '').lower() == doi.lower()]
    if len(existing_ids) == 0:
        existing_ids = None
    return existing_ids


def validate_bibtex_id(base_id, pdfs, bibtex_entries):
    """Find a unique identifier for this bibtex entry and PDF file.
    
    Parameters
    ==========
    base_id : str
      A starting point for this ID. If it's already taken, 'base_id-2'
      will be tried, then 'base_id-3', etc.
    pdfs : iterable
      Filenames of existing PDF's, for example from
    ``os.path.listdir()`` to be check for existing IDs.
    bibtex : iterable
      Bibtex entries (dicts) to be checked for a unique ID.
    
    Returns
    =======
    new_id : str
      The new, unique identifier for this entry.
    
    """
    # Helper function
    def id_is_taken(this_id, pdf_ids, bibtext_ids):
        return (this_id in pdf_ids or this_id in bibtex_ids)
    # Prepare lists of existing IDs
    stripped_pdfs = [os.path.splitext(pdf)[0] for pdf in pdfs]
    bibtex_ids = [entry['ID'] for entry in bibtex_entries]
    # Iterate through all the indices and check for available IDs
    idx = 2
    new_id = base_id
    while id_is_taken(new_id, stripped_pdfs, bibtex_ids):
        new_id = "{}-{}".format(base_id, idx)
        idx += 1
    return new_id


def add_bibtex_entry(bibtex, bibtexfile):
    """Add some metadata to an open bibtex file.
    
    Parameters
    ==========
    bibtex : dict
      The bibtex string that will be added to the new bibtex entry.
    bibtexfile : file-like object
      An open, writable, text-mode file (ideally, ``mode='a+'``). The
      new bibtex entry will be added to the end.
    
    """
    # Save the new tex in the bibtex file
    bibtexfile.seek(0, os.SEEK_END)
    bibtexfile.write('\n')
    bibtexfile.write(bibtex)


def fetch_doi(doi, bibfile, pdf_dir, bibtex_id=None, retrieve_pdf=True):
    """Retrieve a document by its Digital object idetifier.
    
    This function will retrieve metadata and optionally the PDF for
    the requested document. A new entry will be added to the bibtex
    file with a unique ID and, if requested, the PDF will be added to
    the ``pdf_dir`` with a filename matching the new ID.
    
    Parameters
    ==========
    doi : str
      The digital object identifier for the object.
    bibfile : File-like object
      An open, writable (``mode='a+'``), text-mode file that will
      receive the new bibtex entry.
    pdf_dir : str
      Directory in which to put the PDF.
    bibtex_id : str
      The requested bibtex ID for this document. Will not necessarily
      be the one that is used if that ID is already taken.
    retrieve_pdf : bool
      Whether to attempt to download the PDF of the document (default,
      True).
    
    Returns
    =======
    new_id : str
      The bibtex ID for the new entry.
    
    """
    # Read in the existing bibtex entries
    bibfile.seek(0)
    bibdb = bibtexparser.loads(bibfile.read() + ' ')
    # Create the article class
    article = Article(doi=doi)
    # Retrieve the article metdata
    metadata = article.metadata()
    # Check if the entry already exists in the refs file
    _existing_ids = existing_ids(doi=doi, bib_entries=bibdb.entries)
    if _existing_ids:
        raise exceptions.DuplicateDOIError(
            "Existing entries found for DOI '{}': {}".format(doi, _existing_ids))
    # Determine a unique ID for this entry/PDF
    default_id = bibtex_id if bibtex_id is not None else article.default_id()
    new_id = validate_bibtex_id(base_id=default_id,
                                pdfs=os.listdir(pdf_dir),
                                bibtex_entries=bibdb.entries)
    # Download the PDF
    if retrieve_pdf:
        pdffile = os.path.join(pdf_dir, '{}.pdf'.format(new_id))
        try:
            pdffp = open(pdffile, 'wb')
            article.download_pdf(fp=pdffp)
        except:
            # Delete the file if an exception occurred
            pdffp.close()
            os.remove(pdffile)
            raise
        else:
            # Upon successful download, just close the file
            pdffp.close()
    # Add the bibtex entry to the bibfile
    bibtex = article.bibtex(id=new_id)
    add_bibtex_entry(bibtex, bibfile)
    return new_id


def main(argv=None):
    # Prepare the command line arguments
    parser = argparse.ArgumentParser(
        description='Fetch an article by its digital object identifier'
    )
    parser.add_argument('doi', type=str,
                        help='the digital object identifier to retrieve')
    parser.add_argument('-p', '--pdf-dir', dest='pdf_dir', default='./papers/',
                        metavar='PATH',
                        help='where to store the downloaded PDF')
    parser.add_argument('-b', '--bibtex-file', dest='bibfile', default='./refs.bib',
                        metavar='FILE',
                        help='will add the new bibtex entry to this file')
    parser.add_argument('-i', '--bibtex-id', dest='bibtex_id', default=None,
                        help="a default bibtex id, but may be modified if it already exists")
    parser.add_argument('--no-pdf', dest='retrieve_pdf', action='store_false',
                        help="don't attempt to download the article as a PDF")
    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help="show detailed debug information via the logging platform")
    parser.add_argument('-f', '--force', dest='force', action='store_true',
                        help="force creation of files, directories, etc.")
    # Parse the command line arguments
    args = parser.parse_args(argv)
    # Start logging
    debug = args.debug
    if debug:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    logging.basicConfig(level=level)
    doi = parse_doi(args.doi)
    force = args.force
    bibfile = args.bibfile
    bibtex_id = args.bibtex_id
    pdf_dir = args.pdf_dir
    retrieve_pdf = args.retrieve_pdf
    # Check if the file exists
    if not os.path.exists(bibfile) and not force:
        raise exceptions.BibtexFileNotFoundError("Cannot find bibtex file: {}".format(bibfile))
    # Check if the PDF directory exists
    if not os.path.exists(pdf_dir) and retrieve_pdf:
        if force:
            os.makedirs(pdf_dir)
        else:
            raise exceptions.BibtexFileNotFoundError("Cannot find PDF folder: {}".format(pdf_dir))
    # Do the actual DOI fetching
    logging.debug("Opening bibfile '%s'", bibfile) 
    with open(bibfile, mode='a+') as bibfp:
        new_id = fetch_doi(doi=doi, bibfile=bibfp, pdf_dir=pdf_dir,
                           bibtex_id=bibtex_id, retrieve_pdf=retrieve_pdf)
    # Confirm successful retrieval
    msg = "Saved entry as {} ({}.pdf)".format(new_id, os.path.join(pdf_dir, new_id))
    log.info(msg)
    print("Saved entry as {} ({}.pdf)".format(new_id, os.path.join(pdf_dir, new_id)))


if __name__ == '__main__':
    main()
