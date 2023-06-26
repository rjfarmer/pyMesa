import pyMesa as pym


const_lib,const_def = pym.loadMod("const")


print(const_def.a2rad)
print(const_def.thermohaline_mixing)
print(const_def.mev_to_ergs)


ierr=0
const_lib.const_init(pym.MESA_DIR,ierr)
print(const_def.mev_to_ergs)
