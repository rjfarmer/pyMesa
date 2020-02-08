import pyMesaUtils as pym

const_lib, const_def = pym.loadMod("const")
if pym.MESA_VERSION < 12608:
	crlibm_lib, _ = pym.loadMod("crlibm")
	crlibm_lib.crlibm_init()
else:
	crlibm_lib, _ = pym.loadMod("math")
	crlibm_lib.math_init()
ierr=0
const_lib.const_init(pym.MESA_DIR,ierr)

atm_lib, atm_def = pym.loadMod("atm")

atm_lib.atm_l(5777.0,1.0)
