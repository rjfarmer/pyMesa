import pyMesa as pym

const_lib, const_def = pym.loadMod("const")
math_lib, _ = pym.loadMod("math")
math_lib.math_init()
ierr=0
const_lib.const_init(pym.MESA_DIR,ierr)

chem_lib,chem_def = pym.loadMod("chem")


chem_lib.chem_init('isotopes.data',ierr)
