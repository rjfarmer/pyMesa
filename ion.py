import pyMesaUtils as pym
import numpy as np

const_lib, const_def = pym.loadMod("const")
crlibm_lib, _ = pym.loadMod("crlibm")
ion_lib, ion_def = pym.loadMod("ionization")

ierr=0

crlibm_lib.crlibm_init()
const_lib.const_init(pym.MESA_DIR,ierr)


res = ion_lib.ionization_init('ion','',pym.ION_CACHE,False,ierr)


Z = 0.02
X = 0.78
Rho = 10**9
log10Rho = np.log10(Rho)
T = 10**9
log10T = np.log10(T)
res = np.zeros(ion_def.num_ion_vals.get())
ierr = 0

res = ion_lib.eval_ionization(Z, X, Rho, log10Rho, T, log10T, res, ierr)

