import pyMesaUtils as pym

const_lib, const_def = pym.loadMod("const")
crlibm_lib, _ = pym.loadMod("crlibm")
crlibm_lib.crlibm_init()
ierr=0
const_lib.const_init(pym.MESA_DIR,ierr)

atm_lib, atm_def = pym.loadMod("atm")

atm_lib.eval_lrad(1.0,1.0,1.0,1.0,1.0,1.0)
