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
        result = fetch_doi.is_duplicate(doi='10.1021/acs.chemmater.6b05114',
                                        bib_entries=self.sample_bibtex)
        self.assertTrue(result)
    
    def test_no_duplicate(self):
        result = fetch_doi.is_duplicate(doi='gibberish doi',
                                        bib_entries=self.sample_bibtex)
        self.assertFalse(result)

    def test_no_doi(self):
        sample_bibtex = [
            {
                'ID': 'wolf2017',
            }
        ]
        result = fetch_doi.is_duplicate(doi='gibberish doi',
                                        bib_entries=sample_bibtex)
        self.assertFalse(result)


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
        try:
            os.mkdir(pdfdir)
            fetch_doi.fetch_doi(doi='10.1021/acs.chemmater.6b05114',
                                pdf_dir='papers/',
                                bibfile=bibfile)
        finally:
            shutil.rmtree(pdfdir)
            pass
        print(bibfile.getvalue())
            
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
            fetch_doi.main(['10.1021/acs.chemmater.6b05114'])
        finally:
            shutil.rmtree('./papers/')
            os.remove('refs.bib')
