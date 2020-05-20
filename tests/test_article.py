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

import bibtexparser

from franklin import Article, exceptions


class ArticlesTests(unittest.TestCase):
    perspective_paper_doi = '10.1021/acs.chemmater.6b05114'
    def test_doi_url(self):
        article = Article(doi=self.perspective_paper_doi)
        real_url = 'http://pubs.acs.org/doi/10.1021/acs.chemmater.6b05114'
        self.assertEqual(article.url(), real_url)
    
    def test_doi_url(self):
        doi = 'sdflkj'
        article = Article(doi=doi)
        with self.assertRaises(exceptions.DOIError):
            article.url()
    
    def test_pdf(self):
        article = Article(doi=self.perspective_paper_doi)
        output_fp = io.BytesIO()
        # Retrieve the actual PDF
        pdf = article.download_pdf(fp=output_fp)
        # Check that a valid PDF was returned
        output_fp.seek(0)
        self.assertEqual(output_fp.read(8).decode(), '%PDF-1.5')
        # Clean up
        output_fp.close()
    
    def test_bibtex(self):
        article = Article(doi=self.perspective_paper_doi)
        bibtex = article.bibtex()
        bibtex = bibtexparser.loads(bibtex)
        self.assertEqual(len(bibtex.entries), 1)
        bibdict = bibtex.entries[0]
        self.assertEqual(bibdict['doi'], self.perspective_paper_doi)
        self.assertEqual(bibdict['author'], 'Mark Wolf and Brian M. May and Jordi Cabana')
        self.assertEqual(bibdict['publisher'], 'American Chemical Society ({ACS})')
        self.assertEqual(bibdict['journal'], 'Chemistry of Materials')
        self.assertEqual(bibdict['year'], '2017')
        self.assertEqual(bibdict['ID'], 'cabana2017')
        # Now try with a custom ID
        new_bibdict = bibtexparser.loads(article.bibtex(id='wolf2017')).entries[0]
        self.assertEqual(new_bibdict['ID'], 'wolf2017')
    
    def test_metadata(self):
        article = Article(doi=self.perspective_paper_doi)
        metadata = article.metadata()
        self.assertEqual(metadata['doi'], self.perspective_paper_doi)
        self.assertNotIn('ID', metadata.keys())
    
    def test_author(self):
        article = Article(doi=self.perspective_paper_doi)
        self.assertEqual(article.authors()[0], 'Mark Wolf')
        self.assertEqual(article.authors()[1], 'Brian M. May')
        self.assertEqual(article.authors()[2], 'Jordi Cabana')

    def test_default_id(self):
        article = Article(doi=self.perspective_paper_doi)
        self.assertEqual(article.default_id(), 'cabana2017')
