import unittest
import io

import orgparse

from franklin import orgmode


class DedupeTests(unittest.TestCase):
    orgtext = (
        "* Research papers\n"
        "** My Paper \n"
        "   :PROPERTIES:\n"
        "   :Custom_ID: chen2020\n"
        "   :Read: false\n"
        "   :END:\n"
        "   [[papers:chen2020][chen2020-paper]]\n"
        "** My Paper :tag1:tag2:\n"
        "   :PROPERTIES:\n"
        "   :Custom_ID: chen2020\n"
        "   :Read: false\n"
        "   :END:\n"
        "   [[papers:chen2020][chen2020-paper]]\n"
        "   Now I've added some notes\n"
        "** Some other paper\n"
        "   :PROPERTIES:\n"
        "   :Custom_ID: chen2021\n"
        "   :Read: false\n"
        "   :END:\n"
        "   [[papers:chen2021][chen2021-paper]]\n"
        "** Some other paper\n"
        "   :PROPERTIES:\n"
        "   :Custom_ID: chen2021\n"
        "   :Read: false\n"
        "   :END:\n"
        "   [[papers:chen2021][chen2021-paper]]\n"
        "** Random heading\n"
    )
    
    def test_dedupe_notes(self):
        orgfile = io.StringIO(self.orgtext)
        exact_ids, inexact_ids = orgmode.dedupe_notes(orgfile)
        self.assertEqual(exact_ids, ['chen2021'])
        self.assertEqual(inexact_ids, ['chen2020'])
    
    def test_find_duplicates(self):
        duped_list = [3, 7, 3, 8, 10, 3, 8]
        dupes = orgmode.find_duplicates(duped_list)
        self.assertEqual(dupes, [3, 8])
    
    def test_nodes_are_equal(self):
        orgtree = orgparse.loads(self.orgtext)
        unequal_nodes = orgtree.children[0].children[:2]
        equal_nodes = orgtree.children[0].children[2:4]
        self.assertFalse(orgmode.nodes_are_equal(*unequal_nodes))
        self.assertTrue(orgmode.nodes_are_equal(*equal_nodes))
