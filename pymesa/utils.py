import pymesa.pyMesaUtils as pym

class utils(object):
    def __init__(self):
        self.const_lib, self.const_def = pym.loadMod("const")
        
        self.crlibm_lib, _ = pym.loadMod("math")
        self.crlibm_lib.math_init()
        
        self.utils_lib, self.utils_def = pym.loadMod("utils")
