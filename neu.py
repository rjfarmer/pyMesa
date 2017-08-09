import pyMesaUtils as pym

neu_lib,neu_def = pym.loadMod("neu")


flags=np.zeros(neu_def.num_neu_types)
flags[:]=True

sources=np.zeros((neu_def.num_neu_types,neu_def.num_neu_rvs))
info=0
neu_lib.neu_get(10**9,9.0,10**7.0,7.0,1.0,1.0,1.0,7.5,flags,sources,info)
