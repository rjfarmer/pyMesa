import pyMesaUtils as pym

const_lib, const_def = pym.loadMod("const")
crlibm_lib, _ = pym.loadMod("crlibm")
crlibm_lib.crlibm_init()
ierr=0
const_lib.const_init(pym.MESA_DIR,ierr)

chem_lib,chem_def = pym.loadMod("chem")
