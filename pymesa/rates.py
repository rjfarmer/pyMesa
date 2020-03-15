import pymesa.pyMesaUtils as pym
import matplotlib.pyplot as plt
import numpy as np

from . import const
from . import math
from . import rates

class rates(object):
    def __init__(self, defaults):        
        self.const = const.const(defaults)
        self.math = math.math(defaults)
        self.chem = chem.chem(defaults)
    
        self.rates_lib, self.rates_def = pym.loadMod("rates",defaults)
        self.rates_lib.rates_init(defaults['reactionlist_filename'],defaults['jina_reaclib_filename'],
                    defaults['rates_table_dir_in'],defaults['use_suzuki_weak_rates'],
                    defaults['special_weak_states_file'],defaults['special_weak_transitions_file'],
                    defaults['rates_cache_dir'],0)


    def show_raw_rates(self,rate='r_c12_ag_o16'):
        """
        Get raw rate

        """

        rate_id=rates_lib.rates_reaction_id(rate)

        logT=np.linspace(7.0,10.0,10000)
        r=[]
        for lt in logT:
             temp=10**lt
             tf={}
             res=self.rates_lib.eval_tfactors(tf, lt, temp)
             tf=res['tf']
             raw_rate=0
             ierr=0    
             res = self.rates_lib.get_raw_rate(1, c12o16_id, temp, tf, raw_rate, ierr)
             r.append(res['raw_rate'])

        plt.plot(logT,np.log10(r))
        plt.show()
        
    def get_rate_from_cache(self,rate):
        return self.rates_lib.show_reaction_rates_from_cache(os.path.join(pym.RATES_CACHE,rate),ierr)


# # Get screening factors
# max_z_to_cache = 2
# sc = {}
# temp = 10**9
# logT = np.log10(temp)
# den = 10**9
# logRho = np.log10(den)
# zbar = 1.0
# abar = 1.0
# z2bar = 1.0
# screening_mode = rates_lib.screening_option('extended',ierr)
# graboske_cache = np.zeros((3,max_z_to_cache,max_z_to_cache))
# num_isos = 2
# theta_e  = 1.0

# y = np.array([0.5/1.0,0.5/4.0])
# iso_z = np.array([1.0,2.0])

# sc_res = rates_lib.screen_set_context( 
            # sc, temp, den, logT, logRho, zbar, abar, z2bar,  
            # screening_mode, graboske_cache,  
            # theta_e, num_isos, y, iso_z)

  
# sc = sc_res['sc']
# a1 = 1.0
# z1 = 1.0
# a2 = 4.0
# z2 = 2.0



# zg1 = 0
# zg2 = 0
# zg3 = 0
# zg4 = 0
# zs13 = 0
# zhat = 0
# zhat2 = 0
# lzav = 0
# aznut = 0
# zs13inv = 0
# ierr = 0
# res = rates_lib.screen_init_AZ_info( 
               # a1, z1, a2, z2, 
               # zg1, zg2, zg3, zg4, zs13, 
               # zhat, zhat2, lzav, aznut, zs13inv, 
               # ierr)

# zg1 = res['zg1']
# zg2 = res['zg2']
# zg3 = res['zg3']
# zg4 = res['zg4']
# zs13 = res['zs13']
# zhat = res['zhat']
# zhat2 = res['zhat2']
# lzav = res['lzav']
# aznut = res['aznut']
# zs13inv = res['zs13inv']
# ierr = 0

# scor = 0
# scordt = 0
# scordd = 0

# theta_e_for_graboske_et_al = theta_e

# screen_res = rates_lib.screen_pair( 
               # sc, a1, z1, a2, z2, screening_mode, 
               # zg1, zg2, zg3, zg4, zs13, zhat, zhat2, lzav, aznut, zs13inv, 
               # theta_e_for_graboske_et_al, graboske_cache, scor, scordt, scordd, ierr)






