import os
import logging
import re
import argparse
from functools import lru_cache

from html.parser import HTMLParser
import requests
import bibtexparser
import tqdm

from . import exceptions


log = logging.getLogger(__name__)


local_abbreviations = {
    'the journal of small papers': 'J. Sm. Papers',
    'materials today nano': 'Mater. Today Nano',
    'materials today': 'Mater. Today',
    'advanced energy materials': 'Adv. Energy Mater.',
    'advanced materials': 'Adv. Mater.',
    'journal of applied physics': 'J. Appl. Phys.',
    'journal of materials chemistry a': 'J. Mater. Chem. A',
    'chemical communications': 'Chem. Commun.',
    'ieee transactions on systems, man, and cybernetics': 'IEEE Transactions on Systems, Man, and Cybernetics',
    'ieee computer graphics and applications': 'IEEE Computer Graphics and Applications',
    'ieee signal processing letters': 'IEEE Signal Processing Letters',
    'ieee transactions on image processing': 'IEEE Transactions on Image Processing',
    'ieee signal processing magazine': 'IEEE Signal Processing Magazine',
    'ieee transactions on pattern analysis and machine intelligence': 'IEEE Transactions on Pattern Analysis and Machine Intelligence',
    'ieee transactions on visualization and computer graphics': 'IEEE Transactions on Visualization and Computer Graphics',
    'analytical chemistry': 'Anal. Chem.',
    'science': 'Science',
    'nature': 'Nature',
    'advanced functional materials': 'Adv. Funct. Mater.',
    'electrochemistry': 'Electrochemistry',
    'advanced materials interfaces': 'Adv. Mater. Interfaces',
    'chemical reviews': 'Chem. Rev.',
    'journal of energy storage': 'J. Energy Storage',
    'atomic data and nuclear data tables': 'At. Data Nucl. Data Tables',
    'radiation physics and chemistry': 'Radiat. Phys. Chem.',
    'materials characterization': 'Mater. Charact.',
    'inorganic chemistry': 'Inorg. Chem.',
    'journal of physics d: applied physics': 'J. Phys. D',
    'frontiers in energy research': 'Front. Energy Res.',
    'journal of physics: condensed matter': 'J. Phys. Condens. Matter',
    'energy storage materials': 'Energy Storage Mater.',
    'spie newsroom': 'SPIE Newsroom',
    'journal of polymer science, part b: polymer physics': 'J. Polym. Sci., Part B: Polym. Phys.',
    'environmental science & technology': 'Environ. Sci. Technol.',
    'journal of electronic imaging': 'J. Electron. Imaging',
}


class CassiAbbreviation():
    span_re = re.compile('<span style="background-color:#7FFFD4">([^<]*)</span>')
    whitespace_re = re.compile('\s+')
    class SearchParser(HTMLParser):
        journals = ... # Set in __init__
        coden_re = re.compile('([A-Z]+)_TVALUE')
        title_re = re.compile('<a href="publication.jsp')
        _current_coden = None
        _current_block = None
        _current_journal = None
        TITLE = 'title'
        CODEN = 'coden'
        ABBREVIATION = 'abbreviation'
        
        def __init__(self, *args, **kwargs):
            self.journals = []
            super().__init__(*args, **kwargs)
        
        def _switch_blocks(self, new_block):
            if new_block == self.TITLE:
                self._current_journal = ''
            self._current_block = new_block
        
        def handle_starttag(self, tag, attrs):
            attrs = {key: val for key, val in attrs}
            # Look for a valid CODEN
            coden_match = self.coden_re.search(attrs.get('id', ''))
            if coden_match:
                self._current_coden = coden_match.group(1)
                self._switch_blocks(self.CODEN)
            # We're inside the title section
            elif tag == 'a' and 'publication.jsp' in attrs.get('href', ''):
                self._switch_blocks(self.TITLE)
            # We're inside the abbreviation section
            elif tag == 'td' and attrs.get('class', '') == 'valueAbbr':
                self._switch_blocks(self.ABBREVIATION)
        
        def handle_endtag(self, tag):
            if tag == 'tr':
                self._switch_blocks(None)
        
        def handle_data(self, data):
            if self._current_block == self.TITLE and data.strip():
                self._current_journal += data.strip()
            elif self._current_block == self.ABBREVIATION and data.strip():
                # We found the abbreviation, so now reset everything
                abbr = data.strip()
                new_journal = {
                    'title': self._current_journal,
                    'abbreviation': abbr,
                    'coden': self._current_coden,
                }
                self.journals.append(new_journal)
                self._current_journal = None
                self._current_coden = None
    
    def parse_multiple_sources(self, html_response, journal):
        # Sort through the HTML
        parser = self.SearchParser()
        parser.feed(html_response)
        # See if the requested journal is in the parsed data
        matched_journals = [j for j in parser.journals if j['title'].lower() == journal.lower()]
        if len(matched_journals) == 0:
            raise KeyError(f"Could not find CASSI entry for '{journal}'.")
        if len(matched_journals) > 1:
            print(parser.journals)
            raise exceptions.CassiError(f"Found {len(matched_journals)} CASSI entries for "
                                        f"'{journal}'.")
        else:
            abbr = matched_journals[0]['abbreviation']
        return abbr
    
    def parse_single_source(self, html_response, journal):
        # Search the return response for the abbreviated title
        r_str = ('<tr><td class="name">Abbreviated Title</td>'
                 '<td class="value">(?:<span [^>]+>)?'
                 '([-_:A-Za-z0-9. ]+)'
                 '(?:</span>)?</td></tr>')
        match = re.search(r_str, html_response)
        if match:
            abbr = match.group(1)
        else:
            raise exceptions.CassiError(f"Could not parse single hit for '{journal}'")
        return abbr
    
    @lru_cache()
    def __getitem__(self, journal):
        """Retrieve abbreviated journal name from CASSI."""
        # Ask for a validation code for having accepted the terms of service
        cookies = {'UserAccepted': 'YES'}
        response = requests.get('https://cassi.cas.org/search.jsp', cookies=cookies)
        content = str(response.content)
        if 'You have to enable JavaScript' in content:
            raise exceptions.CASSIError("Could not accept CASSI terms.")
        # Extract the validation code from the response
        r_str = '<input type="hidden" name="c" value="([^"]+)"'
        match = re.search(r_str, content)
        if match:
            c_code = match.group(1)
        else:
            raise exceptions.CASSIError("Could not extract CASSI terms validation code.")
        # Perform the actual search
        post_data = {'searchIn': 'titles',
                     'searchFor': journal,
                     'c': c_code}
        if '&' not in journal:
            post_data['exactMatch'] = 'on'
        response = requests.post('https://cassi.cas.org/searching.jsp',
                                 data=post_data)
        # Strip out the background highlighting and extra whitespace
        response_text = self.span_re.sub(r'\1', response.text)
        response_text = self.whitespace_re.sub(r' ', response_text)
        # Deal with multiple similar database hits
        if "Results of Search for" in response_text:
            abbr = self.parse_multiple_sources(response_text, journal)
        else:
            abbr = self.parse_single_source(response_text, journal)
        return abbr


def abbreviate_journals(bibfile: str, output: str=None, use_local=True, use_cassi=True):
    """Parse a bibtex file and abbreviate journal titles.
    
    Parameters
    ==========
    bibfile
      The input bibtex file (open file object) to be parsed.
    output
      The open bibtex file object to receive the parsed bibtex
      content.
    use_local
      Use the built-in database of journal abbreviations.
    use_cassi
      Use the ACS CASSI database of journal abbreviations.
    
    """
    # Build a list of which databases to query
    abbr_dbs = []
    if use_local:
        abbr_dbs.append(local_abbreviations)
    if use_cassi:
        abbr_dbs.append(CassiAbbreviation())
    olddb = bibtexparser.load(bibfile)
    newdb = bibtexparser.bibdatabase.BibDatabase()
    for entry in tqdm.tqdm(olddb.entries):
        if 'journal' in entry.keys():
            journal = entry['journal']
        else:
            continue
        # Clean up the journal title a little
        journal = journal.strip()
        if journal.lower()[0:3] == 'the':
            journal = journal[4:]
        journal = journal.replace('\&', '&').replace('{', '').replace('}', '')
        journal = journal.replace('\ ', ' ').replace('\n', ' ')
        # Do the lookup in each database
        for abbrs in abbr_dbs:
            try:
                entry['journal'] = abbrs[journal.lower()]
            except KeyError:
                continue
            except exceptions.CassiError as e:
                log.warning(e)
            else:
                break
        else:
            log.warning(f"Could not abbreviate journal '{journal}'.")
        newdb.entries.append(entry)
    # Save the updated bibtext database to the new file
    bibtexparser.dump(newdb, output)


def abbreviate_journals_cli(argv=None):
    # Parse the arguments
    parser = argparse.ArgumentParser(description='Abbreviate journal titles in a Bibtex file.')
    parser.add_argument('bibfile', help='bibtex input file')
    parser.add_argument('-o', '--output', help='bibtex input file')
    parser.add_argument('-f', '--force', help='Overwrite existing output file.',
                        action='store_true')
    parser.add_argument('-l', '--no-local', dest='use_local', action='store_false',
                        help='Do not query the local database.')
    parser.add_argument('-c', '--no-cassi', dest='use_cassi', action='store_false',
                        help='Do not query the CASSI database.')
    parser.add_argument('--logfile', help='file to receive the debug log')
    args = parser.parse_args(argv)
    # Prepare logging
    logging.basicConfig(filename=args.logfile)
    # Get a default output filename if necessary
    output = args.output
    if output is None:
        base, ext = os.path.splitext(args.bibfile)
        output = f'{base}-abbrev{ext}'
    # Check if the file exists
    if os.path.exists(output) and not args.force:
        raise exceptions.FileExistsError(
            f"Output file '{output}' already exists. Use `--force` to overwrite.")
    # Call the actual function
    with open(args.bibfile, mode='r') as bibfile, open(output, mode='w') as output:
        abbreviate_journals(bibfile=bibfile, output=output, use_local=args.use_local,
                            use_cassi=args.use_cassi)
