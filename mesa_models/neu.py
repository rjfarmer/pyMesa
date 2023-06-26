import pyMesa as pym

import numpy as np

math_lib, _ = pym.loadMod("math")
math_lib.math_init()

neu_lib,neu_def = pym.loadMod("neu")


T=10**9.0
log10_T=np.log10(T)
Rho=10**9.0
log10_Rho=np.log10(T)
abar=1.0
zbar=1.0
z2bar=1.0
log10_Tlim=7.5
flags=np.zeros(neu_def.num_neu_types)
flags[:]=True
loss=np.zeros(neu_def.num_neu_rvs)
sources=np.zeros((neu_def.num_neu_types,neu_def.num_neu_rvs))
info=0

res = neu_lib.neu_get(T, log10_T, Rho, log10_Rho, abar, zbar, z2bar, log10_Tlim, flags, loss, sources, info)
