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


from franklin import publishers

import logging
logging.basicConfig(level=logging.DEBUG)


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
        pdf = publishers.electrochemical_society(doi=doi, url=url)
        pdf_header = pdf[:8]
        self.assertEqual(pdf_header, b'%PDF-1.4')
    
    def test_elsevier(self):
        doi = '10.1016/j.jssc.2019.05.006'
        pdf = publishers.elsevier(doi=doi, api_key='')
        pdf_header = pdf[:8]
        self.assertEqual(pdf_header, b'%PDF-1.7')
    
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
