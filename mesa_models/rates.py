import pyMesa as pym

import numpy as np
import os
import matplotlib.pyplot as plt


const_lib, const_def = pym.loadMod("const")
math_lib, _ = pym.loadMod("math")
math_lib.math_init()
chem_lib, chem_def = pym.loadMod("chem")
rates_lib, rates_def = pym.loadMod("rates")

ierr=0

const_lib.const_init(pym.MESA_DIR,ierr)
chem_lib.chem_init('isotopes.data',ierr)

rates_lib.rates_init('reactions.list','jina_reaclib_results_20171020_default',
                    'rate_tables',False,False,'','',pym.RATES_CACHE,ierr)

ierr=0

# Get raw rate

rates_lib.show_reaction_rates_from_cache(os.path.join(pym.RATES_CACHE,'r_c12_ag_o16_1.bin'),ierr)

c12o16_id=rates_lib.rates_reaction_id('r_c12_ag_o16').result

logT=np.linspace(7.0,10.0,1000)
r=[]
for lt in logT:
     temp=10**lt
     tf={}
     res=rates_lib.eval_tfactors(tf, lt, temp)
     tf=res.args['tf']
     raw_rate=0
     ierr=0    
     res = rates_lib.get_raw_rate(c12o16_id, temp, tf, raw_rate, ierr)
     r.append(res.args['raw_rate'])

plt.plot(logT,np.log10(r))
plt.show()



