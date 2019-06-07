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

import bibtexparser

from .article import Article
from . import exceptions


def is_duplicate(doi, bib_entries):
    """Look through a bibtex bibliography and check for duplicate entry.
    
    Parameters
    ==========
    doi : str
      The digital object identifier to search for.
    bib_entries : list
      The bibliography data to look in.
    
    Returns
    =======
    is_duplicate : bool
      True if the doi was found in the bibtex bibliography, otherwise
      False.
    
    """
    is_duplicate = doi in [e['doi'] for e in bib_entries]
    return is_duplicate


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


def fetch_doi(doi, bibfile, pdf_dir, retrieve_pdf=True):
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
    if is_duplicate(doi=doi, bib_entries=bibdb.entries):
        raise exceptions.DuplicateDOIError("Existing entry found for {}".format(doi))
    # Determine a unique ID for this entry/PDF
    new_id = validate_bibtex_id(base_id=article.default_id(),
                                pdfs=os.listdir(pdf_dir),
                                bibtex_entries=bibdb.entries)
    # Download the PDF
    pdffile = os.path.join(pdf_dir, '{}.pdf'.format(new_id))
    with open(pdffile, 'wb') as pdffp:
        article.download_pdf(fp=pdffp)
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
    parser.add_argument('--no-pdf', dest='retrieve_pdf', action='store_false',
                        help="don't attempt to download the article as a PDF")
    # Parse the command line arguments
    args = parser.parse_args(argv)
    doi = args.doi
    bibfile = args.bibfile
    pdf_dir = args.pdf_dir
    retrieve_pdf = args.retrieve_pdf
    # Check if the file exists
    if not os.path.exists(bibfile):
        raise exceptions.BibtexFileNotFoundError("Cannot find bibtex file: {}".format(bibfile))
    # Do the actual DOI fetching
    with open(bibfile, mode='a+') as bibfp:
        new_id = fetch_doi(doi=doi, bibfile=bibfp, pdf_dir=pdf_dir, retrieve_pdf=retrieve_pdf)
    print("Saved entry as {} ({}.pdf)".format(new_id, os.path.join(pdf_dir, new_id)))


if __name__ == '__main__':
    main()
