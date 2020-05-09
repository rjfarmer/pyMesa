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
        self.eos_lib.eos_init(defaults['eosDT_cache_dir'],defaults['eosPT_cache_dir'],
                defaults['eosDE_cache_dir'],defaults['eos_use_cache'],0)
                
        self.eos_handle = self.eos_lib.alloc_eos_handle(0).result
        
        
    def __del__(self):
        if 'eos_lib' in self.__dict__:
            self.eos_lib.eos_shutdown()
            
        
        
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
        z53bar = comp['z53bar']

        net_iso = np.arange(1,species+1)
    
        res = np.zeros(self.eos_def.num_eos_basic_results)
        d_dlnRho_const_T = np.zeros(self.eos_def.num_eos_basic_results)
        d_dlnT_const_Rho = np.zeros(self.eos_def.num_eos_basic_results)
        d_dabar_const_TRho = np.zeros(self.eos_def.num_eos_basic_results)
        d_dzbar_const_TRho = np.zeros(self.eos_def.num_eos_basic_results)
        ierr = 0

        eos_res = self.eos_lib.eosdt_get(
               self.eos_handle, Z, X, abar, zbar, z53bar,
               species, ids, net_iso, xa, 
               Rho, log10Rho, T, log10T, 
               res, d_dlnRho_const_T, d_dlnT_const_Rho, 
               d_dabar_const_TRho, d_dzbar_const_TRho, ierr)         
               
        pym.error_check(eos_res)
         
        output = {}
        output['res'] = self.unpackEosBasicResults(eos_res.args['res'])
        output['d_dlnrho_const_t'] = self.unpackEosBasicResults(eos_res.args['d_dlnrho_const_t'])
        output['d_dlnt_const_rho'] = self.unpackEosBasicResults(eos_res.args['d_dlnt_const_rho'])
        output['d_dabar_const_trho'] = self.unpackEosBasicResults(eos_res.args['d_dabar_const_trho'])
        output['d_dzbar_const_trho'] = self.unpackEosBasicResults(eos_res.args['d_dzbar_const_trho'])

        return output
       
        
    def getEosDE(self,composition,energy,rho,log10T_guess):
        comp = self.chem.basic_composition_info(composition)
    
        X = comp['xh']
        Z = comp['z']
        abar = comp['abar']
        zbar = comp['zbar']
        species = len(composition)
        ids, xa = self.chem.chem_ids(composition)
        log10Rho = self.const.const_def.arg_not_provided
        log10E = self.const.const_def.arg_not_provided

        net_iso = np.arange(1,species+1)
    
        res = np.zeros(self.eos_def.num_eos_basic_results)
        d_dlnRho_const_T = np.zeros(self.eos_def.num_eos_basic_results)
        d_dlnT_const_Rho = np.zeros(self.eos_def.num_eos_basic_results)
        d_dabar_const_TRho = np.zeros(self.eos_def.num_eos_basic_results)
        d_dzbar_const_TRho = np.zeros(self.eos_def.num_eos_basic_results)
        dlnT_dlnE_c_Rho = 0
        dlnT_dlnd_c_E = 0
        dlnPgas_dlnE_c_Rho = 0
        dlnPgas_dlnd_c_E = 0
        T = 0
        log10T = 0
        z53bar = comp['z53bar']
        
        ierr = 0

        eos_res = self.eos_lib.eosDE_get(
               self.eos_handle, Z, X, abar, zbar, z53bar, 
               species, ids, net_iso, xa, 
               energy, log10E, rho, log10Rho, log10T_guess,
               T, log10T, res, d_dlnRho_const_T, d_dlnT_const_Rho,
               d_dabar_const_TRho, d_dzbar_const_TRho, 
               dlnT_dlnE_c_Rho, dlnT_dlnd_c_E, 
               dlnPgas_dlnE_c_Rho, dlnPgas_dlnd_c_E, 
               0)
    
        pym.error_check(eos_res)
         
        output = {}
        output['T'] = eos_res['t']
        output['res'] = self.unpackEosBasicResults(eos_res.args['res'])
        output['d_dlnrho_const_t'] = self.unpackEosBasicResults(eos_res.args['d_dlnrho_const_t'])
        output['d_dlnt_const_rho'] = self.unpackEosBasicResults(eos_res.args['d_dlnt_const_rho'])
        output['d_dabar_const_trho'] = self.unpackEosBasicResults(eos_res.args['d_dabar_const_trho'])
        output['d_dzbar_const_trho'] = self.unpackEosBasicResults(eos_res.args['d_dzbar_const_trho'])
        
        output['dlnT_dlnE_c_Rho'] = eos_res.args['d_dzbar_const_trho']
        output['dlnT_dlnd_c_E'] = eos_res.args['dlnT_dlnd_c_E']
        output['dlnPgas_dlnE_c_Rho'] = eos_res.args['dlnPgas_dlnE_c_Rho']
        output['dlnPgas_dlnd_c_E'] = eos_res.args['dlnPgas_dlnd_c_E']

        return output
        
        
    def getEosPT(self,composition,energy,Pgas,T):
        comp = self.chem.basic_composition_info(composition)
    
        X = comp['xh']
        Z = comp['z']
        abar = comp['abar']
        zbar = comp['zbar']
        species = len(composition)
        chem_id, xa = self.chem.chem_ids(composition)
        log10T = self.const.const_def.arg_not_provided
        log10Pgas = self.const.const_def.arg_not_provided
        z53bar = comp['z53bar']
    
        net_iso = np.arange(1,species+1)
    
        res = np.zeros(self.eos_def.num_eos_basic_results)
        d_dlnRho_const_T = np.zeros(self.eos_def.num_eos_basic_results)
        d_dlnT_const_Rho = np.zeros(self.eos_def.num_eos_basic_results)
        d_dabar_const_TRho = np.zeros(self.eos_def.num_eos_basic_results)
        d_dzbar_const_TRho = np.zeros(self.eos_def.num_eos_basic_results)
        
        dlnRho_dlnPgas_const_T = 0
        dlnRho_dlnT_const_Pgas = 0
        Rho = 0
        log10Rho = 0
        
        ierr = 0
    
        eos_res = self.eos_lib.eosPT_get(
               self.eos_handle, Z, X, abar, zbar, z53bar,
               species, chem_id, net_iso, xa, 
               Pgas, log10Pgas, T, log10T, 
               Rho, log10Rho, dlnRho_dlnPgas_const_T, dlnRho_dlnT_const_Pgas, 
               res, d_dlnRho_const_T, d_dlnT_const_Rho, 
               d_dabar_const_TRho, d_dzbar_const_TRho, 0)
    
        pym.error_check(eos_res)
         
        output = {}
        output['rho'] = eos_res['Rho']
        output['dlnRho_dlnPgas_const_T'] = eos_res.args['dlnRho_dlnPgas_const_T']
        output['dlnRho_dlnT_const_Pgas'] = eos_res.args['dlnRho_dlnT_const_Pgas']        
        
        output['res'] = self.unpackEosBasicResults(eos_res.args['res'])
        output['d_dlnrho_const_t'] = self.unpackEosBasicResults(eos_res.args['d_dlnrho_const_t'])
        output['d_dlnt_const_rho'] = self.unpackEosBasicResults(eos_res.args['d_dlnt_const_rho'])
        output['d_dabar_const_trho'] = self.unpackEosBasicResults(eos_res.args['d_dabar_const_trho'])
        output['d_dzbar_const_trho'] = self.unpackEosBasicResults(eos_res.args['d_dzbar_const_trho'])
    
        return output
    
    
    def getEosDT_ideal_gas(self,composition,T,Rho):
        
        comp = self.chem.basic_composition_info(composition)
    
        X = comp['xh']
        Z = comp['z']
        abar = comp['abar']
        zbar = comp['zbar']
        species = len(composition)
        ids, xa = self.chem.chem_ids(composition)
        log10Rho = self.const.const_def.arg_not_provided
        log10T = self.const.const_def.arg_not_provided
        z53bar = comp['z53bar']
    
        net_iso = np.arange(1,species+1)
    
        res = np.zeros(self.eos_def.num_eos_basic_results)
        d_dlnRho_const_T = np.zeros(self.eos_def.num_eos_basic_results)
        d_dlnT_const_Rho = np.zeros(self.eos_def.num_eos_basic_results)
        d_dabar_const_TRho = np.zeros(self.eos_def.num_eos_basic_results)
        d_dzbar_const_TRho = np.zeros(self.eos_def.num_eos_basic_results)
        ierr = 0
    
        eos_res = self.eos_lib.eosDT_ideal_gas_get(
               self.eos_handle, Z, X, abar, zbar, z53bar,
               species, ids, net_iso, xa, 
               Rho, log10Rho, T, log10T, 
               res, d_dlnRho_const_T, d_dlnT_const_Rho, 
               d_dabar_const_TRho, d_dzbar_const_TRho, ierr)
               
        pym.error_check(eos_res)
         
        output = {}
        output['res'] = self.unpackEosBasicResults(eos_res.args['res'])
        output['d_dlnrho_const_t'] = self.unpackEosBasicResults(eos_res.args['d_dlnrho_const_t'])
        output['d_dlnt_const_rho'] = self.unpackEosBasicResults(eos_res.args['d_dlnt_const_rho'])
        output['d_dabar_const_trho'] = self.unpackEosBasicResults(eos_res.args['d_dabar_const_trho'])
        output['d_dzbar_const_trho'] = self.unpackEosBasicResults(eos_res.args['d_dzbar_const_trho'])
    
        return output
         
