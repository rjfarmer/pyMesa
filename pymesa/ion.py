import pymesa.pyMesaUtils as pym
import numpy as np

from . import const
from . import math
from . import chem
from . import eos

class ion(object):
    def __init__(self, defaults):
        self.const = const.const(defaults)
        self.math = math.math(defaults)
            
        self.ion_lib, self.ion_def = pym.loadMod("ionization",defaults)
        self.ion_lib.ionization_init(defaults['file_prefix'],
                        defaults['Z1_suffix'],defaults['ionization_cache_dir'],
                        defaults['ion_use_cache'],0)

        self.eos = eos.eos(defaults)
        self.chem = chem.chem(defaults)

    def getIon(self,T,Rho,Z,X):
        log10Rho = np.log10(Rho)
        log10T = np.log10(T)
        res = np.zeros(self.ion_def.num_ion_vals)
        ierr = 0

        result = self.ion_lib.eval_ionization(Z, X, Rho, log10Rho, T, log10T, res, ierr)
        pym.error_check(result)

        res = result.args['res']
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


    def eval_typical_charge(self, iso, composition, T, Rho):

        eosResult = self.eos.getEosDT(composition,T,Rho)
        free_e = np.exp(eosResult['result']['i_lnfree_e'])

        cid = self.chem.chem_ids({iso:1.0})[0][0]
        abar = self.chem.basic_composition_info({iso:1.0})['abar']

        log10Rho = np.log10(Rho)
        log10T = np.log10(T)

        return self.ion_lib.eval_typical_charge(cid, abar, free_e, T, log10T, Rho, log10Rho)
