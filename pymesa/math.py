import pymesa.pyMesaUtils as pym
import numpy as np


class math(object):
    def __init__(self, defaults):        
        self.math_lib, _ = pym.loadMod("math",defaults)
        self.math_lib.math_init()
