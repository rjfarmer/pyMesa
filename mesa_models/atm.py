import pyMesa as pym

const_lib, const_def = pym.loadMod("const")
math_lib, _ = pym.loadMod("math")
math_lib.math_init()
ierr=0
const_lib.const_init(pym.MESA_DIR,ierr)

atm_lib, atm_def = pym.loadMod("atm")

print(atm_lib.atm_l(5777.0,1.0).result)

atm_lib.atm_shutdown()

