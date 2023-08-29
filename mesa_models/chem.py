import pyMesa as pym

const_lib, const_def = pym.loadMod("const")
math_lib, _ = pym.loadMod("math")
math_lib.math_init()
ierr=0
const_lib.const_init(pym.MESA_DIR,ierr)

chem_lib,chem_def = pym.loadMod("chem")


chem_lib.chem_init('isotopes.data',ierr)


for iso in ['c12','c13','c14']:
    print(f"{iso} {chem_lib.lodders03_element_atom_percent(iso).result}%")



chem_lib.chem_shutdown()