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

from unittest import TestCase, mock
import io
import os

import bibtexparser

from franklin import journals


class JournalTests(TestCase):
    bib_in = (
        "@article{small,"
        "author = {Freely, I.P.},"
        "title = {A small paper},"
        "journal = {The journal of small papers},"
        "year = 1997,"
        "volume = {-1},"
        "note = {to appear},"
        "}"
    )
    
    def test_no_abbreviate_journal(self):
        """Check what happens if there's no journal to abbreviate."""
        pass
    
    def test_abbreviate_journal_local(self):
        bibfile = io.StringIO(self.bib_in)
        out_file = io.StringIO()
        journals.abbreviate_journals(bibfile=bibfile, output=out_file, use_local=True, use_cassi=False)
        # Check that the output
        out_file.seek(0)
        bibdb = bibtexparser.load(out_file)
        self.assertEqual(bibdb.entries[0]['journal'], 'J. Sm. Papers')
    
    def test_cassi_single_hit(self):
        """Test what happens if only one journal returns a match."""
        cassi = journals.CassiAbbreviation()
        response = cassi['Journal of Physical Chemistry C']
        self.assertEqual(response, 'J. Phys. Chem. C')
        response = cassi['J. Phys. Chem. C']
        self.assertEqual(response, 'J. Phys. Chem. C')
        response = cassi['Electrochemical and Solid-State Letters']
        self.assertEqual(response, 'Electrochem. Solid-State Lett.')
    
    def test_cassi_multi_hit(self):
        """Test what happens if multiple journals return matches."""
        cassi = journals.CassiAbbreviation()
        # response = cassi['Journal of the American Chemical Society']
        # self.assertEqual(response, 'J. Am. Chem. Soc.')
        # response = cassi['APPLIED RADIATION AND ISOTOPES']
        # self.assertEqual(response, 'Appl. Radiat. Isot.')
        response = cassi['Science in China, Series A: Mathematics, Physics, Astronomy & Technological Sciences']
        self.assertEqual(response, 'Sci. China, Ser. A: Math., Phys., Astron. Technol. Sci.')
    
    def tearDown(self):
        if os.path.exists('test-file-abbrev.bib'):
            os.remove('test-file-abbrev.bib')
    
    @mock.patch('franklin.journals.abbreviate_journals')
    def test_cli(self, abbreviate_journals):
        journals.abbreviate_journals_cli(['/dev/null', '-o', 'test-file-abbrev.bib'])
        abbreviate_journals.assert_called_once()
        output = abbreviate_journals.call_args[1]['output']
        self.assertEqual(output.name, 'test-file-abbrev.bib')
        self.assertTrue(abbreviate_journals.call_args[1]['use_local'])
        self.assertTrue(abbreviate_journals.call_args[1]['use_cassi'])
