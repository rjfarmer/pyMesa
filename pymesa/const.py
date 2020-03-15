import pymesa.pyMesaUtils as pym
import numpy as np

class const(object):
    def __init__(self, defaults):
        self.const_lib, self.const_def = pym.loadMod("const",defaults)
        self.const_lib.const_init(defaults['mesa_dir'],0)
        
