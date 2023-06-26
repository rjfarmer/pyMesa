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
                    'rate_tables',False,False,'','','',ierr)

ierr=0

# Get raw rate

rates_lib.show_reaction_rates_from_cache(os.path.join(pym.RATES_CACHE,'r_c12_ag_o16_1.bin'),ierr)

c12o16_id=rates_lib.rates_reaction_id('r_c12_ag_o16')

logT=np.linspace(7.0,10.0,10000)
r=[]
for lt in logT:
     temp=10**lt
     tf={}
     res=rates_lib.eval_tfactors(tf, lt, temp)
     tf=res['tf']
     raw_rate=0
     ierr=0    
     res = rates_lib.get_raw_rate(1, c12o16_id, temp, tf, raw_rate, ierr)
     r.append(res['raw_rate'])

plt.plot(logT,np.log10(r))
plt.show()


# Get screening factors
max_z_to_cache = 2
sc = {}
temp = 10**9
logT = np.log10(temp)
den = 10**9
logRho = np.log10(den)
zbar = 1.0
abar = 1.0
z2bar = 1.0
screening_mode = rates_lib.screening_option('extended',ierr)
graboske_cache = np.zeros((3,max_z_to_cache,max_z_to_cache))
num_isos = 2
theta_e  = 1.0

y = np.array([0.5/1.0,0.5/4.0])
iso_z = np.array([1.0,2.0])

sc_res = rates_lib.screen_set_context( 
            sc, temp, den, logT, logRho, zbar, abar, z2bar,  
            screening_mode, graboske_cache,  
            theta_e, num_isos, y, iso_z)

  
sc = sc_res['sc']
a1 = 1.0
z1 = 1.0
a2 = 4.0
z2 = 2.0



zg1 = 0
zg2 = 0
zg3 = 0
zg4 = 0
zs13 = 0
zhat = 0
zhat2 = 0
lzav = 0
aznut = 0
zs13inv = 0
ierr = 0
res = rates_lib.screen_init_AZ_info( 
               a1, z1, a2, z2, 
               zg1, zg2, zg3, zg4, zs13, 
               zhat, zhat2, lzav, aznut, zs13inv, 
               ierr)

zg1 = res['zg1']
zg2 = res['zg2']
zg3 = res['zg3']
zg4 = res['zg4']
zs13 = res['zs13']
zhat = res['zhat']
zhat2 = res['zhat2']
lzav = res['lzav']
aznut = res['aznut']
zs13inv = res['zs13inv']
ierr = 0

scor = 0
scordt = 0
scordd = 0

theta_e_for_graboske_et_al = theta_e

screen_res = rates_lib.screen_pair( 
               sc, a1, z1, a2, z2, screening_mode, 
               zg1, zg2, zg3, zg4, zs13, zhat, zhat2, lzav, aznut, zs13inv, 
               theta_e_for_graboske_et_al, graboske_cache, scor, scordt, scordd, ierr)






