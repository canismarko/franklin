"""Utilities for working with org-mode files."""
import logging

import orgparse

log = logging.getLogger(__name__)


def find_duplicates(arr):
    """Return a list of duplicate entries in *arr*."""
    seen = {}
    dupes = []
    for x in arr:
        if x not in seen:
            seen[x] = 1
        else:
            if seen[x] == 1:
                dupes.append(x)
            seen[x] += 1
    return dupes


def nodes_are_equal(*nodes):
    are_equal = True
    attrs_to_test = ['heading', 'tags', 'properties']
    differing_attrs = []
    for i, this_node in enumerate(nodes):
        for other_node in nodes[i+1:]:
            for attr in attrs_to_test:
                if getattr(this_node, attr) != getattr(other_node, attr):
                    log.debug("Found difference in %s", attr)
                    are_equal = False
                    differing_attrs.append(attr)
    return are_equal, differing_attrs


def dedupe_notes(orgdata):
    """Remove duplicate entries in an org-mode file."""
    orgtree = orgparse.load(orgdata)
    # Flatten the org tree so we can see level 2 nodes
    nodes_lvl1 = [child for parent in orgtree.children for child in parent.children]
    this_node = nodes_lvl1[0]
    ids_lvl1 = [node.properties['Custom_ID'] for node in nodes_lvl1 if 'Custom_ID' in node.properties]
    # Go through each node that appears more than once and see if it's an exact duplicate
    duplicates = find_duplicates(ids_lvl1)
    exact_duplicates = []
    inexact_duplicates = []
    for nodeid in duplicates:
        duplicate_ids = [n for n in nodes_lvl1 if n.properties.get('Custom_ID') == nodeid]
        is_exact_match, attrs = nodes_are_equal(*duplicate_ids)
        if is_exact_match:
            exact_duplicates.append(nodeid)
        else:
            inexact_duplicates.append("{} ({})".format(nodeid, attrs))
    return exact_duplicates, inexact_duplicates
