import pymesa.pyMesaUtils as pym

import numpy as np


class eos(object):
    def __init__(self):
        self.eos_lib, self.eos_def = pym.loadMod("eos")
        self.const_lib, self.const_def = pym.loadMod("const")
        self.crlibm_lib, _ = pym.loadMod("math")
        self.crlibm_lib.math_init()
        self.chem_lib, self.chem_def = pym.loadMod("chem")
        self.net_lib, self.net_def = pym.loadMod("net")
        self.rates_lib, self.rates_def = pym.loadMod("rates")
        self.const_lib.const_init(pym.MESA_DIR,0)
        self.chem_lib.chem_init('isotopes.data',0)

        self.rates_lib.rates_init('reactions.list','jina_reaclib_results_20130213default2',
                    'rate_tables',False,'','','',0)

        self.net_lib.net_init(0)
        self.eos_lib.eos_init('mesa','','','',False,0)
                
        self.eos_handle = self.eos_lib.alloc_eos_handle(0)


    # def getEosDT(Z,X,abar,zbar):
        # chem_h1 = chem_def.ih1.get()

        # net_h1 = net_lib.ih1.get()

        # Z = 0.00
        # X = 1.00
        # abar = 1.0
        # zbar = 1.0
        # species = 1
        # chem_id = np.array([chem_h1])
        # net_iso = np.array([net_h1])
        # xa = np.array([1.0])
        # Rho = 10**8.0
        # log10Rho = 8.0
        # T = 10**9
        # log10T = 9.0
        # res = np.zeros(eos_def.num_eos_basic_results.get())
        # d_dlnRho_const_T = np.zeros(eos_def.num_eos_basic_results.get())
        # d_dlnT_const_Rho = np.zeros(eos_def.num_eos_basic_results.get())
        # d_dabar_const_TRho = np.zeros(eos_def.num_eos_basic_results.get())
        # d_dzbar_const_TRho = np.zeros(eos_def.num_eos_basic_results.get())
        # ierr = 0

        # eos_res = eos_lib.eosdt_get(
               # eos_handle, Z, X, abar, zbar, 
               # species, chem_id, net_iso, xa, 
               # Rho, log10Rho, T, log10T, 
               # res, d_dlnRho_const_T, d_dlnT_const_Rho, 
               # d_dabar_const_TRho, d_dzbar_const_TRho, ierr)
               
        # return eos_res
               
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








