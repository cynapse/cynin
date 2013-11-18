# -*- coding: utf-8 -*-
"""
The wordprocessing module handles a WordprocessingML Open XML document (read *.docx)
"""
# $Id: wordprocessing.py 6800 2007-12-04 11:17:01Z glenfant $

import document
from utils import IndexableTextExtractor
import contenttypes as ct


class WordprocessingDocument(document.Document):
    """Handles specific features of a WordprocessingML document"""

    _extpattern_to_mime = {
        '*.docx': ct.CT_WORDPROC_DOCX_PUBLIC,
        '*.docm': ct.CT_WORDPROC_DOCM_PUBLIC,
        '*.dotx': ct.CT_WORDPROC_DOTX_PUBLIC,
        '*.dotm': ct.CT_WORDPROC_DOTM_PUBLIC
        }

    _text_extractors = (
        IndexableTextExtractor(ct.CT_WORDPROC_DOCUMENT, 'wordprocessing-main:t'),
        )

    pass
