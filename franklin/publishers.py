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
from . import __version__


default_headers = {
    'User-Agent': 'franklin/{} (https://github.com/canismarko/franklin)'.format(__version__),
}


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
        'The Electrochemical Society': iop,
        '{IOP}': iop,
        'Elsevier {BV}': elsevier,
        'Springer Science and Business Media {LLC}': springer,
        'Royal Society of Chemistry ({RSC})': royal_society_of_chemistry,
        'Wiley': wiley,
        'Annual Reviews': annual_reviews,
        'Institute of Electrical and Electronics Engineers ({IEEE})': ieee,
        'American Association for the Advancement of Science ({AAAS})': aaas,
    }
    try:
        pub_func = _pub_dict[publisher]
    except KeyError:
        msg = '"{}" (hint: use `--no-pdf` to skip PDF retrieval)'.format(publisher)
        raise UnknownPublisherError(msg) from None
    return pub_func


def american_chemical_society(doi, *args, **kwargs):
    pdf_url = "https://pubs.acs.org/doi/pdf/{doi}".format(doi=doi)
    pdf_response = requests.get(pdf_url, headers=default_headers)
    # Verify that it's a valid PDF
    if not re.match('%PDF-([-0-9]+)', pdf_response.text[:8]):
        # Failed, so figure out why
        if "Missing resource" in pdf_response.text:
            raise PDFNotFoundError("No PDF for {}".format(doi))
    return pdf_response.content


def aaas(doi, *args, **kwargs):
    # Go resolve the url to extract the AAAS article ID
    html_url = 'https://www.sciencemag.org/lookup/doi/{}'.format(doi)
    response = requests.options(html_url)
    article_re = re.match('https?://[a-z.]+/content/([0-9/]+)', response.url)
    article_id = article_re.group(1)
    # Get the PDF of the article
    pdf_url = "https://science.sciencemag.org/content/{id}.full.pdf".format(id=article_id)
    pdf_response = requests.get(pdf_url, headers=default_headers)
    # Verify that it's a valid PDF
    if not re.match('%PDF-([-0-9]+)', pdf_response.text[:8]):
        # Failed, so figure out why
        if "Missing resource" in pdf_response.text:
            raise PDFNotFoundError("No PDF for {}".format(doi))
    return pdf_response.content



def electrochemical_society(doi, *args, **kwargs):
    # Resolve the DOI to an ECS identifier
    lookup_url = 'http://jes.ecsdl.org/lookup/doi/{}'.format(doi)
    response = requests.get(lookup_url, allow_redirects=False, headers=default_headers)
    ecs_path = response.headers['Location']
    # Retrieve the PDF
    pdf_url = "http://jes.ecsdl.org/{}.full.pdf".format(ecs_path)
    pdf_response = requests.get(pdf_url, headers=default_headers)
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
    headers = default_headers.copy()
    headers.update({
        'Accept': 'application/pdf',
        'apiKey': api_key,
    })
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
    pdf_response = requests.get(pdf_url, headers=default_headers)
    # Verify that it's a valid PDF
    if not re.match('%PDF-([-0-9]+)', pdf_response.text[:8]):
        # Failed, so figure out why
        raise PDFNotFoundError("No PDF for {}".format(doi))
    return pdf_response.content


def royal_society_of_chemistry(doi, url, *args, **kwargs):
    pdf_url = "https://pubs.rsc.org/en/content/articlepdf/2019/sc/c9sc03417j"
    pdf_url = "https://pubs.rsc.org/en/content/articlepdf/2019/sc/c9sc03417j"
    # Determine RSC url for the PDF
    response = requests.get(url, allow_redirects=False, headers=default_headers)
    new_url = response.headers['Location']
    url_regex = 'https://pubs.rsc.org/en/content/articlelanding/([0-9a-zA-Z/]+)/?'
    match = re.match(url_regex, new_url)
    if match:
        rsc_id = match.group(1)
        pdf_url = "https://pubs.rsc.org/en/content/articlepdf/{}".format(rsc_id)
    else:
        raise PDFNotFoundError("Could not parse article URL: '%s' with regex '%s'" % (new_url, url_regex))
    # Retrieve the actual PDF
    pdf_response = requests.get(pdf_url, headers=default_headers)
    # Verify that it's a valid PDF
    if not re.match('%PDF-([-0-9]+)', pdf_response.text[:8]):
        # Failed, so figure out why
        raise PDFNotFoundError("No PDF for {}".format(doi))
    return pdf_response.content


def wiley(doi, *args, **kwargs):
    pdf_url = "https://onlinelibrary.wiley.com/doi/pdfdirect/{}".format(doi)
    pdf_response = requests.get(pdf_url, headers=default_headers)
    # Verify that it's a valid PDF
    if not re.match('%PDF-([-0-9]+)', pdf_response.text[:8]):
        # Failed, so figure out why
        raise PDFNotFoundError("No PDF for {}".format(doi))
    return pdf_response.content


def annual_reviews(doi, *args, **kwargs):
    pdf_url = 'https://www.annualreviews.org/doi/pdf/{}'.format(doi)
    pdf_response = requests.get(pdf_url)
    # Verify that it's a valid PDF
    if not re.match('%PDF-([-0-9]+)', pdf_response.text[:8]):
        # Failed, so figure out why
        raise PDFNotFoundError("No PDF for {}".format(doi))
    return pdf_response.content


def ieee(doi, url, *args, **kwargs):
    # Get the PDF URL from the HTML page
    html_response = requests.get(url)
    html_regex = '"pdfPath":"([^"]+)"'
    html_re = re.search(html_regex, html_response.text)
    if html_re:
        pdf_url = 'https://ieeexplore.ieee.org{}'.format(html_re.group(1))
    else:
        raise PDFNotFoundError("Could not parse article URL: '%s' with regex '%s'" % (url, html_regex))
    # This is a kludge to fix a typo(?) in a specific file
    pdf_url = pdf_url.replace('iel7', 'ielx7')
    # Now retrieve the PDF itself
    pdf_response = requests.get(pdf_url)
    # Verify that it's a valid PDF
    if not re.match('%PDF-([-0-9]+)', pdf_response.text[:8]):
        # Failed, raise a more helpful exception
        raise PDFNotFoundError("No PDF for {}".format(doi))
    return pdf_response.content


def iop(doi, *args, **kwargs):
    pdf_url = f'https://iopscience.iop.org/article/{doi}/pdf'
    pdf_response = requests.get(pdf_url, headers=default_headers)
    # Verify that it's a valid PDF
    if not re.match('%PDF-([-0-9]+)', pdf_response.text[:8]):
        # Failed, so figure out why
        if "you are a bot" in pdf_response.text:
            raise PDFNotFoundError("Captcha detected while retrieving PDF for {}. ".format(doi) + 
                                   "(hint: use `--no-pdf` to skip PDF retrieval)")
        else:
            raise PDFNotFoundError("No PDF for {}. (hint: use `--no-pdf` to skip PDF retrieval)".format(doi))
    return pdf_response.content
    
