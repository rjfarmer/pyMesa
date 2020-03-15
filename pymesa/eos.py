import pymesa.pyMesaUtils as pym

import numpy as np


from . import const
from . import math
from . import chem

class eos(object):
    def __init__(self, defaults):
        self.const = const.const(defaults)
        self.math = math.math(defaults)
        self.chem = chem.chem(defaults)

        self.eos_lib, self.eos_def = pym.loadMod("eos",defaults)
        self.eos_lib.eos_init(defaults['eos_file_prefix'],
                defaults['eosDT_cache_dir'],defaults['eosPT_cache_dir'],
                defaults['eosDE_cache_dir'],defaults['eos_use_cache'],0)
                
        self.eos_handle = self.eos_lib.alloc_eos_handle(0)


    def getEosDT(self,composition,T,Rho):
        
        comp = self.chem.basic_composition_info(composition)
    
        X = comp['xh']
        Z = comp['z']
        abar = comp['abar']
        zbar = comp['zbar']
        species = len(composition)
        ids, xa = self.chem.chem_ids(composition)
        log10Rho = self.const.const_def.arg_not_provided
        log10T = self.const.const_def.arg_not_provided

        net_iso = np.arange(1,species+1)
    
        res = np.zeros(self.eos_def.num_eos_basic_results)
        d_dlnRho_const_T = np.zeros(self.eos_def.num_eos_basic_results)
        d_dlnT_const_Rho = np.zeros(self.eos_def.num_eos_basic_results)
        d_dabar_const_TRho = np.zeros(self.eos_def.num_eos_basic_results)
        d_dzbar_const_TRho = np.zeros(self.eos_def.num_eos_basic_results)
        ierr = 0

        eos_res = self.eos_lib.eosdt_get(
               self.eos_handle, Z, X, abar, zbar, 
               species, ids, net_iso, xa, 
               Rho, log10Rho, T, log10T, 
               res, d_dlnRho_const_T, d_dlnT_const_Rho, 
               d_dabar_const_TRho, d_dzbar_const_TRho, ierr)
         
        output = {}
        output['res'] = self.unpackEosBasicResults(eos_res['res'])
        output['d_dlnrho_const_t'] = self.unpackEosBasicResults(eos_res['d_dlnrho_const_t'])
        output['d_dlnt_const_rho'] = self.unpackEosBasicResults(eos_res['d_dlnt_const_rho'])
        output['d_dabar_const_trho'] = self.unpackEosBasicResults(eos_res['d_dabar_const_trho'])
        output['d_dzbar_const_trho'] = self.unpackEosBasicResults(eos_res['d_dzbar_const_trho'])

        return output
        
    def unpackEosBasicResults(self,array):
        res = {}
        
        if len(array)==1:
            return array[0]
        
        i_lnPgas = self.eos_def.i_lnPgas - 1
        i_lnE  = self.eos_def.i_lnE - 1
        i_lnS = self.eos_def.i_lnS - 1
        i_mu = self.eos_def.i_mu - 1
        i_lnfree_e = self.eos_def.i_lnfree_e - 1
        i_eta = self.eos_def.i_eta - 1
        i_grad_ad = self.eos_def.i_grad_ad - 1
        i_chiRho = self.eos_def.i_chiRho - 1
        i_chiT = self.eos_def.i_chiT - 1
        i_Cp = self.eos_def.i_Cp - 1
        i_Cv = self.eos_def.i_Cv - 1
        i_dE_dRho = self.eos_def.i_dE_dRho - 1
        i_dS_dT = self.eos_def.i_dS_dT - 1
        i_dS_dRho = self.eos_def.i_dS_dRho - 1
        i_gamma1 = self.eos_def.i_gamma1 - 1
        i_gamma3 = self.eos_def.i_gamma3 - 1 
        
        res['i_lnPgas'] = array[i_lnPgas]
        res['i_lnE'] = array[i_lnE]
        res['i_lnS'] = array[i_lnS]
        res['i_mu'] = array[i_mu]
        res['i_lnfree_e'] = array[i_lnfree_e]
        res['i_eta'] = array[i_eta]
        res['i_grad_ad'] = array[i_grad_ad]
        res['i_chiRho'] = array[i_chiRho]
        res['i_chiT'] = array[i_chiT]
        res['i_Cp'] = array[i_Cp]
        res['i_Cv'] = array[i_Cv]
        res['i_dE_dRho'] = array[i_dE_dRho]
        res['i_dS_dT'] = array[i_dS_dT]
        res['i_dS_dRho'] = array[i_dS_dRho]
        res['i_gamma1'] = array[i_gamma1]
        res['i_gamma3'] = array[i_gamma3]        
        
        return res
       
               
    # def getEosHelm():
        # include_radiation = False
        # always_skip_elec_pos = False
        # always_include_elec_pos = False
        # helm_res = np.zeros(eos_def.num_helm_results.get())
         # eos_helm_res = eos_lib.eosDT_HELMEOS_get( 
                   # eos_handle, Z, X, abar, zbar, 
                   # species, chem_id, net_iso, xa, 
                   # Rho, log10Rho, T, log10T, 
                   # include_radiation, always_skip_elec_pos, always_include_elec_pos, 
                   # res, d_dlnRho_const_T, d_dlnT_const_Rho, 
                   # d_dabar_const_TRho, d_dzbar_const_TRho, helm_res, ierr)


        # # The EOS call returns the quantities we want in the "res" array.
        # res = eos_helm_res["res"]
        # # These are indexed by indices that can be found in eos/public/eos_def.f
        # # We can get those indices with calls like this:
        # i_lnE = eos_def.i_lnE.get() - 1
        # # subtract 1 due to the difference between fortran and numpy indexing.

        # IE = np.exp(res[i_lnE])
        # print("Internal Energy from HELM: ", IE, " erg/g")








