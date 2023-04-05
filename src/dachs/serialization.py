# -*- coding: utf-8 -*-
# serialization.py

"""
Utility function to serialize data and meta classes for export, to a HDF5 file, for example.
"""

__author__ = "Ingo Breßler"
__contact__ = "dev@ingobressler.net"
__license__ = "GPLv3+"
__date__ = "2023/02/07"
__status__ = "beta"

from pathlib import PurePosixPath


def dumpKV(prefix: PurePosixPath, objlst, lvl=0):
    """Serializes the given hierarchical DACHS structure as key-value pairs (a dict).
    :param prefix: A word to prepended to all generated keys, a top-level name.
    :param objlst: A hierarchical instance for traversal.
    :param lvl: The current level of invocation, tracks the recursion depth for debugging.
    """
    # handle unnamed lists by default, catch single objects here
    if type(objlst) not in (list, tuple):
        objlst = (objlst,)
    pathlst = {}
    # indent = "".join(["  " for _ in range(lvl)])
    for idx, obj in enumerate(objlst):
        idx = getattr(obj, "ID", idx)
        # print(indent, "=>", idx, obj)
        subpath = PurePosixPath(prefix)
        if len(objlst) > 1:  # we have more than one item
            subpath /= str(idx)
        if hasattr(obj, "_storeKeys"):
            for mem in getattr(obj, "_storeKeys", ()):
                # print(indent, "->", mem, len(objlst))
                items = {(subpath / m): v for m, v in dumpKV(mem, getattr(obj, mem), lvl + 1).items()}
                pathlst.update(items)
        else:
            pathlst.update({subpath: obj})
    return pathlst
