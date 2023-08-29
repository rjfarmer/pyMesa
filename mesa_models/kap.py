import pyMesa as pym

import numpy as np

eos_lib, eos_def = pym.loadMod("eos")
const_lib, const_def = pym.loadMod("const")
math_lib, _ = pym.loadMod("math")
math_lib.math_init()
chem_lib, chem_def = pym.loadMod("chem")
kap_lib,kap_def = pym.loadMod("kap")

ierr=0


const_lib.const_init('',ierr)  
chem_lib.chem_init('isotopes.data', ierr)

eos_lib.eos_init(pym.EOSDT_CACHE, True, ierr)
kap_lib.kap_init(True, pym.KAP_CACHE, ierr)


# Create a kap namelist, this is the easiest way to set
# the options

kap_inlist = 'kap.inlist'
with open(kap_inlist,'w') as f:
    print('&kap',file=f)
    # Set options here
    print('zbase = 0.02',file=f)
    print('/',file=f)

ierr = 0
res = kap_lib.alloc_kap_handle_using_inlist(kap_inlist, ierr)

if res.args['ierr'] != 0:
    raise ValueError("Ierr not zero from alloc kap_handle")

kap_handle = res.result


# 50/50 mix of H/he
species = 2
chem_id = np.array([chem_def.ih1,chem_def.ihe4])
net_iso = np.array([1,2])
xa = np.array([0.5,0.5])
logRho = 8.0
logT = 8.0

# evaluate EOS for lnfree_e and eta and their derivatives

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


lnfree_e = eos_result.args['res'][eos_def.i_lnfree_e-1]
d_lnfree_e_dlnRho = eos_result.args['d_dlnd'][eos_def.i_lnfree_e-1]
d_lnfree_e_dlnT = eos_result.args['d_dlnt'][eos_def.i_lnfree_e-1]

eta = eos_result.args['res'][eos_def.i_eta-1]
d_eta_dlnRho = eos_result.args['d_dlnd'][eos_def.i_eta-1]
d_eta_dlnT = eos_result.args['d_dlnt'][eos_def.i_eta-1]


frac_Type2 = 0.0
kap = 0.0
kap_fracs = np.zeros(kap_def.num_kap_fracs)
dlnkap_dlnRho = 0.0
dlnkap_dlnT = 0.0
dlnkap_dxa = np.zeros(species)
ierr = 0

kap_res = kap_lib.kap_get(kap_handle, species, chem_id, net_iso, xa,
                          logRho, logT,
                          lnfree_e, d_lnfree_e_dlnRho, d_lnfree_e_dlnT,
                          eta, d_eta_dlnRho, d_eta_dlnT,
                          kap_fracs, kap, dlnkap_dlnRho, dlnkap_dlnT, dlnkap_dxa,
                          ierr)

if res.args['ierr'] != 0:
    raise ValueError("Ierr not zero from kap_get")

print(f"Opacity {kap_res.args['kap']}")


kap_lib.kap_shutdown()

