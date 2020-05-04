import pymesa.pyMesaUtils as pym

from . import const
from . import math
from . import chem

class kap(object):
    def __init__(self, defaults):
        self.defaults = defaults
        self.const = const.const(defaults)
        self.math = math.math(defaults)
        self.chem = chem.chem(defaults)
        

        self.kap_lib, self.kap_def = pym.loadMod("kap",defaults)
        self.kap_lib.kap_init(defaults['kap_use_cache'], defaults['kap_cache_dir'],
                                defaults['kap_config_file'], 0)
        

        self.kap_handle = self.kap_lib.alloc_kap_handle(0).result
        self.kap_set_choices()


    def kap_set_choices(self,cubic_interpolation_in_X=False, cubic_interpolation_in_Z=False, 
            include_electron_conduction=True, 
            use_Zbase_for_Type1=True, use_Type2_opacities=True, 
            kap_Type2_full_off_X=0.71, kap_Type2_full_on_X=0.70,
            kap_Type2_full_off_dZ=0.001, kap_Type2_full_on_dZ=0.01, show_info=False):
                
        res = self.kap_lib.kap_set_choices(self.kap_handle,
            self.defaults['kap_file_prefix'],self.defaults['CO_prefixdefaults'],
            self.defaults['lowT_prefix'],
            cubic_interpolation_in_X, cubic_interpolation_in_Z, 
            include_electron_conduction, 
            use_Zbase_for_Type1, use_Type2_opacities,
            kap_Type2_full_off_X, kap_Type2_full_on_X, 
            kap_Type2_full_off_dZ, kap_Type2_full_on_dZ, 
            self.defaults['blend_logT_upper_bdy'],self.defaults['blend_logT_lower_bdy'],
            self.defaults['kap_use_cache'],show_info,
            0
            )
        pym.error_check(res)


    def kap_get(self, zbar, X, Z, Zbase, XC, XN, XO, XNe,logRho,logT,
                lnfree_e, d_lnfree_e_dlnRho, d_lnfree_e_dlnT):
                    
        frac_Type2 = 0.0
        dlnkap_dlnRho = 0.0
        dlnkap_dlnT = 0.0
        k = 0
    
        result = self.kap_lib.kap_get(
            self.kap_handle, zbar, X, Z, Zbase, XC, XN, XO, XNe, logRho, logT, 
            lnfree_e, d_lnfree_e_dlnRho, d_lnfree_e_dlnT, 
            frac_Type2, k, dlnkap_dlnRho, dlnkap_dlnT, 0)
            
        pym.error_check(result)
        
        res = result.args
        
        return {'frac_Type2':res['frac_type2'],'kap':res['kap'],
                'dlnkap_dlnrho':res['dlnkap_dlnrho'], 'dlnkap_dlnt':res['dlnkap_dlnt']}


    def __del__(self):
        if 'kap_lib' in self.__dict__:
            self.kap_lib.kap_shutdown()
        
