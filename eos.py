import pyMesaUtils as pym

eos_lib, eos_def = pym.loadMod("eos")
const_lib, const_def = pym.loadMod("const")
crlibm_lib, _ = pym.loadMod("crlibm")
chem_lib, chem_def = pym.loadMod("chem")

#Nets broken at the momement
#net_lib, net_def = pym.loadMod("net")

crlibm_lib.crlibm_init()
ierr=0
const_lib.const_init(pym.MESA_DIR,ierr)

chem_lib.chem_init(pym.DATA_DIR+'/chem_data/isotopes.data',ierr)


eos_lib.eos_init('mesa','','','',False,ierr)
                
eos_handle = eos_lib.alloc_eos_handle(ierr)


Z = 0
X = 0
abar = 0
zbar = 0
species = 0
chem_id = 0
net_iso = 0
xa = 0
Rho = 0
log10Rho = 0
T = 0
log10T = 0
res = 0
d_dlnRho_const_T = 0
d_dlnT_const_Rho = 0
d_dabar_const_TRho = 0
d_dzbar_const_TRho = 0
ierr = 0

eos_res = eos_lib.eosDT_get( &
               eos_handle, Z, X, abar, zbar, &
               species, chem_id, net_iso, xa, &
               Rho, log10Rho, T, log10T, &
               res, d_dlnRho_const_T, d_dlnT_const_Rho, &
               d_dabar_const_TRho, d_dzbar_const_TRho, ierr)
