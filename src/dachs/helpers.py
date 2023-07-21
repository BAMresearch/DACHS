# -*- coding: utf-8 -*-
# helpers.py

"""
Utility functions
"""

import pandas as pd


def whitespaceCleanup(text):
    if pd.isnull(text):
        return ""
    return " ".join(str(text).split())
