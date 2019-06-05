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

import requests

from .exceptions import DOIError

class Article():
    """A publish research article."""
    _doi_resolution = None
    
    def __init__(self, doi=''):
        self.doi = doi
    
    def url(self):
        """Retrieve the actual URL given the DOI."""
        response = requests.get(f'https://doi.org/api/handles/{self.doi}').json()
        response_code = response['responseCode']
        if response_code == 1:
            url = response['values'][0]['data']['value']
        elif response_code == 100:
            raise DOIError(f"DOI not found: {response['handle']}")
        else:
            raise DOIError(f"Unexpected DOI error {response}")
        return url

    def metadata(self):
        """Retrieve the meta-data for the article."""
        citation = requests.get(f'https://pubs.acs.org/action/showCitFormats?href={self.url()}')
        print(citation.content)
    
    def download_pdf(self):
        """Retrieve the PDF for the given article resource."""
        pdf_url = f"https://pubs.acs.org/doi/pdf/{self.doi}"
        pdf_response = requests.get(pdf_url)
        # Save the PDF
        print(pdf_response.content)
        print(pdf_url)

