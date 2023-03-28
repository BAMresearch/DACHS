#!/usr/bin/env python
# coding: utf-8

"""
Utility function to serialize data and meta classes for export, to a HDF5 file, for example.
"""

__author__ = "Ingo Breßler"
__contact__ = "dev@ingobressler.net"
__license__ = "GPLv3+"
__date__ = "2023/02/07"
__status__ = "beta"

from pathlib import PurePosixPath

def storagePaths(name, objlst):
    prefix = PurePosixPath(name)
    # handle unnamed lists by default, catch single objects here
    if type(objlst) not in (list, tuple):
        objlst = (objlst,)
    pathlst = {}
    for idx, obj in enumerate(objlst):
        for mem in getattr(obj, '_storeKeys', ()):
            pathlst.update(
                {prefix/(str(idx)/m if len(objlst) > 1 else m): v
                for m,v in storagePaths(mem, getattr(obj, mem)).items()})
        if not len(pathlst):
            pathlst.update({prefix:obj})
    return pathlst
