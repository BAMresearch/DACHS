# the following probably shouldn't be in here, because this duplicates code in dachs/__init__


from pint import UnitRegistry


ureg = UnitRegistry()
ureg.define(r"percent=0.01")
ureg.define(r"euro=1=€")
ureg.define(r"dollar=1=$")
ureg.define(r"item=1")
