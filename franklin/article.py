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

import re
import requests
import time
import functools
import logging

import bibtexparser

from .exceptions import DOIError, PDFNotFoundError
from .publishers import get_publisher


log = logging.getLogger(__name__)


def journal_abbreviation(journal):
    """Retrieve abbreviated journal name from CASSI."""
    # Ask for a validation code for having accepted the terms of service
    cookies = {'UserAccepted': 'YES'}
    response = requests.get('https://cassi.cas.org/search.jsp', cookies=cookies)
    content = str(response.content)
    if 'You have to enable JavaScript' in content:
        raise exceptions.CASSIError("Could not accept CASSI terms.")
    # Extract the validation code from the response
    r_str = '<input type="hidden" name="c" value="([^"]+)"'
    match = re.search(r_str, content)
    if match:
        c_code = match.group(1)
    else:
        raise exceptions.CASSIError("Could not extract CASSI terms validation code.")
    # Perform the actual search
    response = requests.post('https://cassi.cas.org/searching.jsp',
                             data={'searchIn': 'titles',
                                   'searchFor': journal,
                                   'exactMatch': 'on',
                                   'c': 'WIy460-R_DY'})
    # Search the return response for the abbreviated title
    r_str = '<tr><td class="name">Abbreviated Title</td><td class="value">([A-Za-z0-9_. ]+)</td></tr>'
    match = re.search(r_str, str(response.content))
    if match:
        abbr = match.group(1)
    else:
        log.warning("Could not abbreviate journal '%s'.", journal)
        abbr = journal
    return abbr

class Article():
    """A publish research article."""
    _doi_resolution = None
    
    def __init__(self, doi=''):
        self.doi = doi
    
    def url(self):
        """Retrieve the actual URL given the DOI."""
        response = requests.get('https://doi.org/api/handles/{doi}'.format(doi=self.doi)).json()
        response_code = response['responseCode']
        if response_code == 1:
            url = response['values'][0]['data']['value']
        elif response_code == 100:
            raise DOIError("DOI not found: {}".format(response['handle']))
        else:
            raise DOIError("Unexpected DOI error {}".format(response))
        return url
    
    @functools.lru_cache()
    def _bibtex(self):
        """Load the raw bibtex from DOI server."""
        headers = {
            'Accept': 'application/x-bibtex',
        }
        bibtex = requests.get('https://dx.doi.org/{doi}'.format(doi=self.doi), headers=headers)
        return bibtex.text
    
    def metadata(self):
        """Retrieve metadata about this article and return as a dictionary."""
        bibtex = self._bibtex()
        bibdb = bibtexparser.loads(bibtex)
        if len(bibdb.entries) != 1:
            msg = "Found {} bibtex entries for DOI: '{}'".format(len(bibdb.entries), self.doi)
            raise DOIError(msg)
        metadata = bibdb.entries[0]
        del metadata['ID']
        return metadata
    
    def bibtex(self, id=None, abbreviate_journal=True):
        """Prepare bibtex entry for this article.
        
        Parameters
        ==========
        id : str
          The entry ID to use. If omitted, ``self.default_id()`` will
          be used.
        abbreviate_journal : bool
          If true, the abbreviated journal name will be retrieved from
          CASSI.
        
        Returns
        =======
        bibtex : str
          The prepared bibtex entry.
        
        """
        metadata = self.metadata()
        metadata['ID'] = id if id is not None else self.default_id()
        # Abbreviate the journal name
        if abbreviate_journal:
            metadata['journal'] = journal_abbreviation(metadata['journal'])
        # Convert to bibtex
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = [metadata]
        bibtex = bibtexparser.dumps(db)
        return bibtex
    
    def download_pdf(self, fp):
        """Retrieve the PDF for the given article resource.
        
        Parameters
        ==========
        fp : File-like object
          Will receive the PDF contents. Must be writable and in a
          binary mode.
        
        """
        metadata = self.metadata()
        get_pdf = get_publisher(metadata['publisher'])
        pdf_response = get_pdf(doi=self.doi, url=self.url())
        # Save the PDF
        fp.write(pdf_response)
    
    def authors(self):
        metadata = self.metadata()
        authors = metadata['author'].split(' and ')
        return authors
    
    def default_id(self):
        """Prepare a default ID suitable for bibtex."""
        first_author = self.authors()[0]
        last_name = first_author.split(' ')[-1].lower()
        default_id = '{last_name}{year}'.format(last_name=last_name,
                                                year=self.metadata()['year'])
        return default_id
        
