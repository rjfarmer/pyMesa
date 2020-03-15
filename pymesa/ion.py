import pymesa.pyMesaUtils as pym
import numpy as np

from . import const
from . import math

class ion(object):
    def __init__(self, defaults):
        self.const = const.const(defaults)
        self.math = math.math(defaults)
            
        self.ion_lib, self.ion_def = pym.loadMod("ionization",defaults)
        self.ion_lib.ionization_init(defaults['file_prefix'],
                        defaults['Z1_suffix'],defaults['ionization_cache_dir'],
                        defaults['ion_use_cache'],0)

    def getIon(self,T,Rho,Z,X):
        log10Rho = np.log10(Rho)
        log10T = np.log10(T)
        res = np.zeros(self.ion_def.num_ion_vals.get())
        ierr = 0

        res = self.ion_lib.eval_ionization(Z, X, Rho, log10Rho, T, log10T, res, ierr)
        res = res['res']
        # Unpack res into a dict
        state = {}
        state['ion_ilogPgas'] = res[self.ion_def.ion_ilogPgas-1]
        
        state['ion_ilogpp_H'] = res[self.ion_def.ion_ilogpp_H-1]
        state['ion_ilogpp_He'] = res[self.ion_def.ion_ilogpp_He-1]
        state['ion_ilogpp_C'] = res[self.ion_def.ion_ilogpp_C-1]
        state['ion_ilogpp_N'] = res[self.ion_def.ion_ilogpp_N-1]
        state['ion_ilogpp_O'] = res[self.ion_def.ion_ilogpp_O-1]
        state['ion_ilogpp_Ne'] = res[self.ion_def.ion_ilogpp_Ne-1]
        state['ion_ilogpp_Mg'] = res[self.ion_def.ion_ilogpp_Mg-1]
        state['ion_ilogpp_Si'] = res[self.ion_def.ion_ilogpp_Si-1]
        state['ion_ilogpp_Fe'] = res[self.ion_def.ion_ilogpp_Fe-1]
        
        state['ion_iZ_H'] = res[self.ion_def.ion_iZ_H-1]
        state['ion_iZ_He'] = res[self.ion_def.ion_iZ_He-1]
        state['ion_iZ_C'] = res[self.ion_def.ion_iZ_C-1]
        state['ion_iZ_N'] = res[self.ion_def.ion_iZ_N-1]
        state['ion_iZ_O'] = res[self.ion_def.ion_iZ_O-1]
        state['ion_iZ_Ne'] = res[self.ion_def.ion_iZ_Ne-1]
        state['ion_iZ_Mg'] = res[self.ion_def.ion_iZ_Mg-1]
        state['ion_iZ_Si'] = res[self.ion_def.ion_iZ_Si-1]
        state['ion_iZ_Fe'] = res[self.ion_def.ion_iZ_Fe-1]
        
        state['ion_ifneut_H'] = res[self.ion_def.ion_ifneut_H-1]
        state['ion_ifneut_He'] = res[self.ion_def.ion_ifneut_He-1]
        state['ion_ifneut_C'] = res[self.ion_def.ion_ifneut_C-1]
        state['ion_ifneut_N'] = res[self.ion_def.ion_ifneut_N-1]
        state['ion_ifneut_O'] = res[self.ion_def.ion_ifneut_O-1]
        state['ion_ifneut_Ne'] = res[self.ion_def.ion_ifneut_Ne-1]
        state['ion_ifneut_Mg'] = res[self.ion_def.ion_ifneut_Mg-1]
        state['ion_ifneut_Si'] = res[self.ion_def.ion_ifneut_Si-1]
        state['ion_ifneut_Fe'] = res[self.ion_def.ion_ifneut_Fe-1]
        
        return state
