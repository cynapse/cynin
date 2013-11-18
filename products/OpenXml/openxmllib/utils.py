# -*- coding: utf-8 -*-
"""
Various utilities for openxmllib
"""
# $Id: utils.py 6800 2007-12-04 11:17:01Z glenfant $

import re
from lxml import etree

from namespaces import ns_map

def xmlFile(path, mode='r'):
    """lxml cannot parse XML files starting with a BOM
    (see http://www.w3.org/TR/2000/REC-xml-20001006 in F.1.)
    In case such XML file is used, we must skip these characters
    So we open all XML files for read with 'xmlFile'.
    TODO: File this issue to lxml ML or tracker (feature or bug ?)
    """

    fh = file(path, mode)
    while fh.read(1) != '<': # Ignoring everything before '<?xml...'
        pass
    fh.seek(-1, 1)
    return fh


def toUnicode(objekt):
    """Safely converts anything returned by lxml services to unicode
    @param objekt: anything
    @return: the object itself if not a string, otherwise the unicode of the string
    """

    if not isinstance(objekt, str):
        return objekt
    return unicode(objekt, 'ascii')



class IndexableTextExtractor(object):

    wordssearch_rx = re.compile(r'\w+', re.UNICODE)
    text_extract_xpath = etree.XPath('text()')

    def __init__(self, content_type, *text_elements):
        """Building the extractor
        @param content_type: content_type of the part for which the extractor is defined
        @param text_elements: default text elements. See self.addTextElement(...)
        """

        self.content_type = content_type
        self.text_elts_xpaths = []
        for te in text_elements:
            self.addTextElement(te)
        return


    def addTextElement(self, element_name):
        """Adding an element that may contanin text to index
        @param element_name: an element that contains text to extract.
             the name may be prefixed with a key from namespaces.ns_map
        """

        self.text_elts_xpaths.append(etree.XPath('//' + element_name, namespaces=ns_map))
        return


    def indexableText(self, tree):
        """Provides the indexable - search engine oriented - raw text
        @param tree: an ElementTreee
        @return: set(["foo", "bar", ...])"
        """

        rval = set()
        root = tree.getroot()
        for txp in self.text_elts_xpaths:
            elts = txp(root)
            texts = [self.text_extract_xpath(elt) for elt in elts]
            # Texts in element may be empty
            texts = [toUnicode(x)[0] for x in texts
                     if len(x) > 0]
            for text in texts:
                words = self.wordssearch_rx.findall(text)
                rval |= set(words)
        return rval

