import pyMesaUtils as pym

# This is broken with the changes to math_lib in ~12608
# For now all you can and should do is call the init function


if pym.MESA_VERSION < 12608:
	crlibm_lib, _ = pym.loadMod("crlibm")
	crlibm_lib.crlibm_init()
else:
	crlibm_lib, _ = pym.loadMod("math")
	crlibm_lib.math_init()


