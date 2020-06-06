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


import unittest
import io

import PyPDF2

from franklin import publishers, exceptions


class PublisherTests(unittest.TestCase):
    def test_config(self):
        config = publishers.load_config()
        self.assertIn('Elsevier', config)
        self.assertIn('api_key', config['Elsevier'])
    
    def test_acs_pdf(self):
        doi = '10.1021/acs.chemmater.6b05114'
        pdf = publishers.american_chemical_society(doi=doi)
        pdf_header = pdf[:8]
        self.assertEqual(pdf_header, b'%PDF-1.5')
    
    def test_electrochemical_society(self):
        doi = '10.1149/2.0011911jes'
        url = 'http://jes.ecsdl.org/lookup/doi/{}'.format(doi)
        pdf = publishers.iop(doi=doi, url=url)
        pdf_header = pdf[:8]
        self.assertEqual(pdf_header, b'%PDF-1.4')
    
    @unittest.skip("Will be rewritten once Elsevier API is dropped.")
    def test_elsevier(self):
        # doi = '10.1016/j.jpowsour.2008.09.090' # <- not open access
        doi = '10.1016/j.jssc.2019.05.006' # <- open access
        pdf_bytes = publishers.elsevier(doi=doi, api_key='')
        pdf_header = pdf_bytes[:8]
        self.assertEqual(pdf_header, b'%PDF-1.7')
        # Check for the right number of pages in PDF
        pdf = PyPDF2.PdfFileReader(io.BytesIO(pdf_bytes))
        self.assertEqual(pdf.getNumPages(), 9)
    
    def test_springer(self):
        doi = '10.1007/s40097-019-0293-x'
        pdf = publishers.springer(doi=doi)
        pdf_header = pdf[:8]
        self.assertEqual(pdf_header, b'%PDF-1.6')
    
    def test_royal_society(self):
        doi = '10.1039/C9SC03417J'
        url = 'http://xlink.rsc.org/?DOI=C9SC03417J'
        pdf = publishers.royal_society_of_chemistry(doi=doi, url=url)
        pdf_header = pdf[:8]
        self.assertEqual(pdf_header, b'%PDF-1.6')
    
    def test_wiley(self):
        doi = "10.1002/open.201900136"
        pdf = publishers.wiley(doi=doi)
        pdf_header = pdf[:8]
        self.assertEqual(pdf_header, b'%PDF-1.6')
    
    def test_annual_reviews(self):
        doi = '10.1146/annurev.physchem.59.032607.093731'
        pdf = publishers.annual_reviews(doi=doi)
        pdf_header = pdf[:8]
        self.assertEqual(pdf_header, b'%PDF-1.4')
    
    def test_ieee(self):
        doi = '10.1109/ACCESS.2019.2941901'
        url = 'https://ieeexplore.ieee.org/document/8840876'
        pdf = publishers.ieee(doi=doi, url=url)
        pdf_header = pdf[:8]
        self.assertEqual(pdf_header, b'%PDF-1.4')
        # Test that a bad url raises an exception
        bad_url = 'https://ieeexplore.ieee.org/fakething/8843852/'
        with self.assertRaises(exceptions.PDFNotFoundError):
            pdf = publishers.ieee(doi=doi, url=bad_url)
    
    def test_aaas(self):
        doi = '10.1126/science.363.6422.11'
        pdf = publishers.aaas(doi=doi)
        pdf_header = pdf[:8]
        self.assertEqual(pdf_header, b'%PDF-1.4')

    def test_iop(self):
        doi = '10.1149/1945-7111/ab6298'
        pdf = publishers.iop(doi=doi)
        pdf_header = pdf[:8]
        self.assertEqual(pdf_header, b'%PDF-1.7')
