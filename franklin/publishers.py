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
import re
import os

import configparser

from .exceptions import PDFNotFoundError, UnknownPublisherError, ConfigError


def load_config():
    """Load the configuration file from disk."""
    config = configparser.ConfigParser()
    config['Elsevier'] = {
        'api_key': '',
    }
    # Read the file from disk
    config.read(os.path.expanduser('~/.franklinrc'))
    return config


def get_publisher(publisher):
    _pub_dict = {
        'American Chemical Society ({ACS})': american_chemical_society,
        'The Electrochemical Society': electrochemical_society,
        'Elsevier {BV}': elsevier,
        'Springer Science and Business Media {LLC}': springer,
    }
    try:
        pub_func = _pub_dict[publisher]
    except KeyError:
        msg = '"{}" (hint: use `--no-pdf` to skip PDF retrieval)'.format(publisher)
        raise UnknownPublisherError(msg) from None
    return pub_func


def american_chemical_society(doi, *args, **kwargs):
    pdf_url = "https://pubs.acs.org/doi/pdf/{doi}".format(doi=doi)
    pdf_response = requests.get(pdf_url)
    # Verify that it's a valid PDF
    if not re.match('%PDF-([-0-9]+)', pdf_response.text[:8]):
        # Failed, so figure out why
        if "Missing resource" in pdf_response.text:
            raise PDFNotFoundError("No PDF for {}".format(doi))
    return pdf_response.content


def electrochemical_society(doi, *args, **kwargs):
    # Resolve the DOI to an ECS identifier
    lookup_url = 'http://jes.ecsdl.org/lookup/doi/{}'.format(doi)
    response = requests.get(lookup_url, allow_redirects=False)
    ecs_path = response.headers['Location']
    # Retrieve the PDF
    pdf_url = "http://jes.ecsdl.org/{}.full.pdf".format(ecs_path)
    pdf_response = requests.get(pdf_url)
    # Verify that it's a valid PDF
    if not re.match('%PDF-([-0-9]+)', pdf_response.text[:8]):
        # Failed, so figure out why
        raise PDFNotFoundError("No PDF for {}".format(doi))
    return pdf_response.content


def elsevier(doi, api_key=None, *args, **kwargs):
    # Make sure the API key is set
    if api_key is None:
        api_key = load_config()['Elsevier']['api_key']
    # Prepare the API request
    api_url = "https://api.elsevier.com/content/article/doi/{doi}?"
    if api_key:
        api_url += "apiKey={key}&"
    api_url = api_url.format(doi=doi, key=api_key)
    headers = {
        'Accept': 'application/pdf',
        'apiKey': api_key
    }
    pdf_response = requests.get(api_url, headers=headers)
    # Verify that it's a valid PDF
    if not re.match('%PDF-([-0-9]+)', pdf_response.text[:8]):
        if not api_key:
            # It probably failed because the API key was not saved
            msg = ("No API key found for Elsevier. See the documentation "
                   "for more info: "
                   "https://franklin.readthedocs.io/en/latest/publishers.html#elsevier")
            raise ConfigError(msg)
        else:
            
            # General failure
            raise PDFNotFoundError("No PDF for {}".format(doi))
    return pdf_response.content


def springer(doi, *args, **kwargs):
    pdf_url = "https://link.springer.com/content/pdf/{doi}.pdf"
    pdf_url = pdf_url.format(doi=doi)
    pdf_response = requests.get(pdf_url)
    # Verify that it's a valid PDF
    if not re.match('%PDF-([-0-9]+)', pdf_response.text[:8]):
        # Failed, so figure out why
        raise PDFNotFoundError("No PDF for {}".format(doi))
    return pdf_response.content
