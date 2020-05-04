import pymesa.pyMesaUtils as pym

from . import const
from . import math


class atm(object):
    def __init__(self, defaults):
        self.const = const.const(defaults)
        self.math = math.math(defaults)

        self.atm_lib,self.atm_def = pym.loadMod("atm",defaults)
        self.atm_lib.init(True, 0)
        
        
    def atm_Teff(self, L, R):
        return self.atm_lib.atm_Teff(L,R).result
        
    def atm_L(self, Teff, R):
        return self.atm_lib.atm_L(Teff,R).result
        
    def atm_black_body_T(self, L, R):
        return self.atm_lib.atm_black_body_T(L,R).result
        
    def __del__(self):
        if 'atm_lib' in self.__dict__:
            self.atm_lib.shutdown()
