import pymesa.pyMesaUtils as pym
import numpy as np


class math(object):
    def __init__(self, defaults):        
        self.math_lib, _ = pym.loadMod("math",defaults)
        self.math_lib.math_init()


    def __dir__(self):
        return dir(self.math_lib)


    def __getattr__(self, x):
        if 'math_lib' in self.__dict__:
            if hasattr(self.math_lib, x):
                return getattr(self.math_lib,x)