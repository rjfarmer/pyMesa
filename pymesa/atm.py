import pymesa.pyMesaUtils as pym


class atm(object):
    def __init__(self):
        self.const_lib, self.const_def = pym.loadMod("const")
        self.crlibm_lib, _ = pym.loadMod("math")
        self.crlibm_lib.math_init()
        self.const_lib.const_init(pym.MESA_DIR,0)
        self.atm_lib,self.atm_def = pym.loadMod("atm")
        self.atm_lib.init(True, 0)
        
        
    def atm_Teff(self, L, R):
        return self.atm_lib.atm_Teff(L,R)
        
    def atm_L(self, Teff, R):
        return self.atm_lib.atm_L(LTeff,R)
        
    def atm_black_body_T(self, L, R):
        return self.atm_lib.atm_black_body_T(L,R)
        
    def __del__(self):
        if 'atm_lib' in self.__dict__():
            self.atm_lib.shutdown()