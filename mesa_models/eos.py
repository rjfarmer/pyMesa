import pyMesa as pym

import numpy as np

eos_lib, eos_def = pym.loadMod("eos")
const_lib, const_def = pym.loadMod("const")
math_lib, _ = pym.loadMod("math")
math_lib.math_init()
chem_lib, chem_def = pym.loadMod("chem")

ierr=0

const_lib.const_init(pym.MESA_DIR,ierr)
chem_lib.chem_init('isotopes.data',ierr)

ierr=0

eos_lib.eos_init(pym.EOSDT_CACHE, True, ierr)
                
eos_inlist = 'eos.inlist'
with open(eos_inlist,'w') as f:
    print('&eos',file=f)
    # Set options here
    print('/',file=f)

ierr = 0
res = eos_lib.alloc_eos_handle_using_inlist(eos_inlist, ierr)

if res.args['ierr'] != 0:
    raise ValueError("Ierr not zero from alloc eos_handle")

eos_handle = res.result

# 50/50 mix of H/he
species = 2
chem_id = np.array([chem_def.ih1,chem_def.ihe4])
net_iso = np.array([1,2])
xa = np.array([0.5,0.5])
logRho = 8.0
logT = 8.0

res = np.zeros(eos_def.num_eos_basic_results)
d_dlnRho = np.zeros(eos_def.num_eos_basic_results)
d_dlnT = np.zeros(eos_def.num_eos_basic_results)
d_dxa = np.zeros((eos_def.num_eos_basic_results,species))

eos_result = eos_lib.eosdt_get(
    eos_handle, species, chem_id, net_iso, xa,
    10**logRho, logRho, 10**logT, logT,
    res, d_dlnRho, d_dlnT, d_dxa, 
    ierr
)

if res.args['ierr'] != 0:
    raise ValueError("Ierr not zero eosdt_get")

# The EOS call returns the quantities we want in the "res" array.
res = eos_result.args["res"]
# These are indexed by indices that can be found in eos/public/eos_def.f90
# We can get those indices with calls like this:
i_lnE = eos_def.i_lne - 1
# subtract 1 due to the difference between fortran and numpy indexing.

IE = np.exp(res[i_lnE])
print("Internal Energy: ", IE, " erg/g")








