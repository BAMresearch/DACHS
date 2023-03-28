# -*- coding: utf-8 -*-
# __init__.py

from pint import UnitRegistry

__version__ = '0.1.0'

ureg = UnitRegistry(auto_reduce_dimensions=True)
ureg.define(r"percent=0.01")
ureg.define(r"euro=1=€")
ureg.define(r"dollar=1=$")
ureg.define(r"item=1")
