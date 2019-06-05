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
        # pdf = article.pdf()
        # self.assertEqual(pdf, '')

    def test_metadata(self):
        article = Article(doi=self.perspective_paper_doi)
        print(article.metadata())
        assert False
    
    # def test_author(self):
    #     article = Article(doi=self.perspective_paper_doi)
    #     self.assertEqual(article.authors[0], 'Mark Wolf')
