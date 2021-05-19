
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
import re

import bibtexparser
import pandas as pd

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
        "@article{irrelevant,"
        "author = {Freely, I.P.},"
        "title = {Shrimp Racing Stats},"
        "journal = {The journal of pointless science},"
        "year = 1950,"
        "volume = {-1},"
        "note = {to appear},"
        "}"        
    )
    
    def test_no_abbreviate_journal(self):
        """Check what happens if there's no journal to abbreviate."""
        book_bib = (
            '@book{groot2008,'
            'author = {Frank de Groot and Akio Kotani},'
            'title = {Core Level Spectroscopy of Solids},'
            'publisher = {CRC Press},'
            'year = 2008,'
            'isbn = {978-0-8493-9071-5}'
        '}')
        bibfile = io.StringIO(book_bib)
        out_file = io.StringIO()
        journals.abbreviate_bibtex_journals(bibfile=bibfile, output=out_file,
                                            use_native=True, use_cassi=False, use_ltwa=False)
        # Make sure that bib entries without a 'journal' are included as is
        out_file.seek(0)
        bibdb = bibtexparser.load(out_file)
        self.assertEqual(bibdb.entries[0]['ID'], 'groot2008')
    
    def test_abbreviate_journal_local(self):
        bibfile = io.StringIO(self.bib_in)
        out_file = io.StringIO()
        journals.abbreviate_bibtex_journals(bibfile=bibfile, output=out_file,
                                            use_native=True, use_cassi=False, use_ltwa=False)
        # Check that the output
        out_file.seek(0)
        bibdb = bibtexparser.load(out_file)
        self.assertEqual(bibdb.entries[1]['journal'], 'J. Sm. Papers')

    def test_latex_aux_file(self):
        bibfile = io.StringIO(self.bib_in)
        out_file = io.StringIO()
        latex_aux_files = [io.StringIO("\citation{small}")]
        journals.abbreviate_bibtex_journals(bibfile=bibfile,
                                            output=out_file,
                                            latex_aux_files=latex_aux_files,
                                            use_native=True,
                                            use_cassi=False,
                                            use_ltwa=False)
        out_file.seek(0)
        bibdb = bibtexparser.load(out_file)
        bad_article_in_list = len([e for e in bibdb.entries if e['ID'] == 'irrelevant']) > 0
        self.assertFalse(bad_article_in_list, "'irrelevant' article found in list.")
    
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
    
    @mock.patch('franklin.journals.abbreviate_bibtex_journals')
    def test_cli(self, abbreviate_bibtex_journals):
        journals.abbreviate_journals_cli(['/dev/null', '-o', 'test-file-abbrev.bib'])
        self.assertEqual(abbreviate_bibtex_journals.call_count, 1)
        output = abbreviate_bibtex_journals.call_args[1]['output']
        self.assertEqual(output.name, 'test-file-abbrev.bib')
        self.assertTrue(abbreviate_bibtex_journals.call_args[1]['use_native'])
        self.assertTrue(abbreviate_bibtex_journals.call_args[1]['use_cassi'])


class LTWATests(TestCase):

    def test_ltwa_list(self):
        ltwa = journals.LTWAAbbreviation()
        df = ltwa.ltwa_list()
        self.assertEqual(df.columns[0], 'WORD')
        self.assertEqual(df.columns[1], 'ABBREVIATIONS')
        self.assertEqual(df.columns[2], 'LANGUAGE CODES')
    
    def test_no_abbreviations(self):
        ltwa = journals.LTWAAbbreviation()
        abbr = ltwa['SPIE Newsroom']
        self.assertEqual(abbr, 'SPIE Newsroom')
    
    def test_abbreviations(self):
        ltwa = journals.LTWAAbbreviation()
        valid_abbrs = {
            'Journal of the american Chemical Society': 'J. Am. Chem. Soc.',
            'nuclear instruments & methods in physics research section a-accelerators spectrometers detectors and associated equipment': 'Nucl. Instrum. Methods In Phys. Res. Sect. A-Accelerators Spectrom. Detect. Assoc. Equip.'
        }
        for (journal, real_abbr) in valid_abbrs.items():
            abbr = ltwa[journal]
            self.assertEqual(abbr, real_abbr)
    
    def test_find_abbrev_in_df(self):
        ltwa = journals.LTWAAbbreviation()
        df = pd.DataFrame([('a-', 'a.', 'en'), ('b-', 'n.a.', 'en'), ('chuck-', 'c.-', 'en'),
                           ('journal', 'j.', 'fre, eng')],
                          columns=['WORD', 'ABBREVIATIONS', 'LANGUAGE CODES'])
        abbrev = ltwa.find_abbrev_in_df('art', df)
        self.assertEqual(abbrev, 'a.')
        # Check a 'n.a.' word
        abbrev = ltwa.find_abbrev_in_df('bowl', df)
        self.assertEqual(abbrev, 'bowl')
        # Check an abbreviation with captured group
        abbrev = ltwa.find_abbrev_in_df('chuckle', df)
        self.assertEqual(abbrev, 'c.le')
        # Check a non-existent word
        abbrev = ltwa.find_abbrev_in_df('dance', df)
        self.assertEqual(abbrev, 'dance')
        # Check a simple non-wildcard match
        abbrev = ltwa.find_abbrev_in_df('journal', df)
        self.assertEqual(abbrev, 'j.')


class TitlecaseTests(TestCase):
    def test_titlecase(self):
        new_title = journals.titlecase('I am not a title')
        self.assertEqual(new_title, 'I Am Not a Title')

    def test_titlecase_texmacro(self):
        new_title = journals.titlecase('evaluation of primary particles of \ce{LiMn2O4}')
        self.assertEqual(new_title, 'Evaluation of Primary Particles of \ce{LiMn2O4}')

    def test_titlecase_newline(self):
        new_title = journals.titlecase('evaluation of primary\nparticles of \ce{LiMn2O4}')
        self.assertEqual(new_title, 'Evaluation of Primary Particles of \ce{LiMn2O4}')


class FixCurlyBracesTests(TestCase):
    def test_no_curly_braces(self):
        entry = {
            'title': 'A normal title',
        }
        journals.fix_curly_braces(entry)
        self.assertEqual(entry['title'], 'A normal title')
    
    def test_bad_curly_braces(self):
        entry = {
            'title': '{A normal title}',
        }
        journals.fix_curly_braces(entry)
        self.assertEqual(entry['title'], 'A normal title')
    
    def test_normal_curly_braces(self):
        entry = {
            'title': 'A {normal} title',
        }
        journals.fix_curly_braces(entry)
        self.assertEqual(entry['title'], 'A {normal} title')
        
    def test_deceptive_curly_braces(self):
        entry = {
            'title': '{A} normal {title}',
        }
        journals.fix_curly_braces(entry)
        self.assertEqual(entry['title'], '{A} normal {title}')
    
    def test_double_deceptive_curly_braces(self):
        entry = {
            'title': '{A {normal} title}',
        }
        journals.fix_curly_braces(entry)
        self.assertEqual(entry['title'], 'A {normal} title')
    
    def test_bad_ending_curly_braces(self):
        entry = {
            'title': '{A normal {title}',
        }
        journals.fix_curly_braces(entry)
        self.assertEqual(entry['title'], 'A normal {title')
