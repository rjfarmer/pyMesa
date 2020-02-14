
import pymesa.pyMesaUtils as pym


class kap(object):
    def __init__(self):
        self.const_lib, self.const_def = pym.loadMod("const")
        
        self.crlibm_lib, _ = pym.loadMod("math")
        self.crlibm_lib.math_init()
        
        self.chem_lib, self.chem_def = pym.loadMod("chem")
        self.chem_lib.chem_init('isotopes.data',0)
        

        self.kap_lib, self.kap_def = pym.loadMod("eos")
        self.kap_lib.kap_init('gs98','gs98_co','lowT_fa05_gs98',3.88,3.80,True,pym.KAP_CACHE,'',False,0)

        self.kap_handle = self.kap_lib.alloc_kap_handle(0)

        self.kap_lib.kap_set_choices(self.kap_handle,False,False,True,True,True,0.71,0.70,0.001,0.01,0)


    def __del__(self):
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
