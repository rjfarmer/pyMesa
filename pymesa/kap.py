import pymesa.pyMesaUtils as pym

from . import const
from . import math
from . import chem

class kap(object):
    def __init__(self, defaults):
        self.const = const.const(defaults)
        self.math = math.math(defaults)
        self.chem = chem.chem(defaults)
        

        self.kap_lib, self.kap_def = pym.loadMod("eos",defaults)
        self.kap_lib.kap_init(defaults['kap_file_prefix'],defaults['CO_prefixdefaults'],
                            defaults['lowT_prefix'],defaults['blend_logT_upper_bdy'],
                            defaults['blend_logT_lower_bdy'],defaults['kap_use_cache'],
                            defaults['kap_cache_dir'], defaults['kap_config_file'],
                            defaults['kap_show_info'], 0
                            )

        self.kap_handle = self.kap_lib.alloc_kap_handle(0)
        self.kap.kap_set_choices()


    def kap_set_choices(self,cubic_interpolation_in_X=False, cubic_interpolation_in_Z=False, 
            include_electron_conduction=True, 
            use_Zbase_for_Type1=True, use_Type2_opacities=True, 
            kap_Type2_full_off_X=0.71, kap_Type2_full_on_X=0.70,
            kap_Type2_full_off_dZ=0.001, kap_Type2_full_on_dZ=0.01):
                
        self.kap_lib.kap_set_choices(self.kap_handle,cubic_interpolation_in_X, 
            cubic_interpolation_in_Z, 
            include_electron_conduction, 
            use_Zbase_for_Type1, use_Type2_opacities,
            kap_Type2_full_off_X, kap_Type2_full_on_X, 
            kap_Type2_full_off_dZ, kap_Type2_full_on_dZ, 
            0
            )

    def __del__(self):
        if 'kap_lib' in self.__dict__:
            self.kap_lib.kap_shutdown()
        
        
    



# handle = kap_handle
# zbar = 1.0
# X = 0.78
# Z = 0.02
# Zbase = 0.02
# XC = 0.0
# XN = 0.0
# XO = 0.0
# XNe = 0.0
# logRho = 9.0
# logT = 9.0
# lnfree_e = 0.0
# d_lnfree_e_dlnRho= 0.0
# d_lnfree_e_dlnT= 0.0
# use_Zbase_for_Type1 = False
# frac_Type2 = 0.0
# kap = 0.0
# dlnkap_dlnRho = 0.0
# dlnkap_dlnT = 0.0
# ierr = 0

# kap_res = self.kap_lib.kap_get(handle, zbar, X, Z, Zbase, XC, XN, XO, XNe, logRho, logT,
            # lnfree_e, d_lnfree_e_dlnRho, d_lnfree_e_dlnT,
            # frac_Type2, kap, dlnkap_dlnRho, dlnkap_dlnT, ierr)
