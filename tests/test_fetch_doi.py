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


from unittest import TestCase
import io
import os
import shutil

from franklin import fetch_doi, exceptions


class IsDuplicateTests(TestCase):
    sample_bibtex = [
        {'ID': 'wolf2017',
         'doi': '10.1021/acs.chemmater.6b05114',
        }
    ]
    
    def test_valid_duplicate(self):
        result = fetch_doi.existing_ids(doi='10.1021/acs.chemmater.6b05114',
                                        bib_entries=self.sample_bibtex)
        self.assertEqual(result, ['wolf2017'])
    
    def test_no_duplicate(self):
        result = fetch_doi.existing_ids(doi='gibberish doi',
                                        bib_entries=self.sample_bibtex)
        self.assertIs(result, None)

    def test_no_doi(self):
        sample_bibtex = [
            {
                'ID': 'wolf2017',
            }
        ]
        result = fetch_doi.existing_ids(doi='gibberish doi',
                                        bib_entries=sample_bibtex)
        self.assertIs(result, None)


class ValidateIDTest(TestCase):
    def test_already_unique_id(self):
        base_id = 'wolf2017'
        new_id = fetch_doi.validate_bibtex_id(base_id, [], '')
        self.assertEqual(new_id, base_id)
    
    def test_id_in_pdfs(self):
        base_id = 'wolf2017'
        new_id = fetch_doi.validate_bibtex_id(base_id, ['wolf2017.pdf'], '')
        self.assertEqual(new_id, 'wolf2017-2')
        # What if the second one is taken too
        base_id = 'wolf2017'
        new_id = fetch_doi.validate_bibtex_id(base_id, ['wolf2017.pdf', 'wolf2017-2.pdf'], '')
        self.assertEqual(new_id, 'wolf2017-3') 
    
    def test_id_in_bibtex(self):
        base_id = 'wolf2017'
        bibtexs = [
            {'ID': 'wolf2017'},
        ]
        new_id = fetch_doi.validate_bibtex_id(base_id, [], bibtexs)
        self.assertEqual(new_id, 'wolf2017-2')
        # What if the second one is taken too
        bibtexs = [
            {'ID': 'wolf2017'},
            {'ID': 'wolf2017-2'},
        ]
        new_id = fetch_doi.validate_bibtex_id(base_id, [], bibtexs)
        self.assertEqual(new_id, 'wolf2017-3') 


class AddBibtexEntryTests(TestCase):
    def test_add_valid_entry(self):
        bibfile = io.StringIO()
        bibtex = ('@article{wolf2017,\n'
                  ' title: {Hello, world},\n'
                  '}')
        fetch_doi.add_bibtex_entry(bibtex, bibfile)
        # Check what was written
        bibfile.seek(0)
        first_line = bibfile.readlines()[1]
        self.assertEqual(first_line.strip(), '@article{wolf2017,')
    
    def test_add_to_existing_file(self):
        bibfile = io.StringIO('Some existing text')
        bibtex = ('@article{wolf2017,\n'
                  ' title: {Hello, world},\n'
                  '}')
        fetch_doi.add_bibtex_entry(bibtex, bibfile)
        # Check what was written
        bibfile.seek(0)
        secondline = bibfile.readlines()[1]
        self.assertEqual(secondline.strip(), '@article{wolf2017,')


class FetchDOITests(TestCase):
    def test_fetch_doi(self):
        bibfile = io.StringIO()
        pdfdir = 'papers/'
        os.mkdir(pdfdir)
        try:
            fetch_doi.fetch_doi(doi='10.1021/acs.chemmater.6b05114',
                                pdf_dir='papers/',
                                bibfile=bibfile)
        finally:
            shutil.rmtree(pdfdir)
            
    def test_duplicate_doi(self):
        bibfile = io.StringIO('@article{wolf2017,'
                              '  doi={10.1021/acs.chemmater.6b05114},'
                              '}')
        with self.assertRaises(exceptions.DuplicateDOIError):
            fetch_doi.fetch_doi(doi='10.1021/acs.chemmater.6b05114',
                                pdf_dir='papers/',
                                bibfile=bibfile)
    
    def test_main(self):
        with open('refs.bib', 'w+') as f:
            f.write(' ')
        os.mkdir('./papers/')
        try:
            fetch_doi.main(['10.1021/acs.chemmater.6b05114', '--bibtex-id', 'wolfman2017'])
        finally:
            shutil.rmtree('./papers/')
            os.remove('refs.bib')

    def test_bibtex_id(self):
        """Test that requesting a bibtex_id honors that request."""
        bibfile = io.StringIO()
        pdfdir = 'papers/'
        os.mkdir(pdfdir)
        requested_id = "wolfman2017"
        try:
            new_id = fetch_doi.fetch_doi(doi='10.1021/acs.chemmater.6b05114',
                                         pdf_dir='papers/',
                                         bibtex_id=requested_id,
                                         bibfile=bibfile)
        finally:
            shutil.rmtree(pdfdir)
        self.assertEqual(new_id, requested_id)


class ParseDOITests(TestCase):
    def test_basic_doi(self):
        new_doi = fetch_doi.parse_doi('10.1021/acs.chemmater.6b05114')
        self.assertEqual(new_doi, '10.1021/acs.chemmater.6b05114')
        # Try one with a colon in the string
        new_doi = fetch_doi.parse_doi('10.1021/acs.chemmater:6b05114')
        self.assertEqual(new_doi, '10.1021/acs.chemmater:6b05114')
    
    def test_doi_in_url(self):
        https_url = 'https://dx.doi.org/10.1021/acs.chemmater.6b05114'
        new_doi = fetch_doi.parse_doi(https_url)
        self.assertEqual(new_doi, '10.1021/acs.chemmater.6b05114')
    
    def test_bad_doi(self):
        with self.assertRaises(exceptions.DOIError):
            fetch_doi.parse_doi('hello')

