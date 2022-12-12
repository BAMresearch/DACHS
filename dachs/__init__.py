from pint import UnitRegistry

ureg = UnitRegistry()
ureg.define(r"percent=0.01")
ureg.define(r"euro=1=€")
ureg.define(r"dollar=1=$")
ureg.define(r"item=1")

from . import _version

__version__ = _version.get_versions()["version"]
