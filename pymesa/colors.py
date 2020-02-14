import pymesa.pyMesaUtils as pym
import numpy as np

class colors(object):
    def __init__(self, defaults=pym.defaults):
        self.const_lib, self.const_def = pym.loadMod("const")
        self.const_lib.const_init(defaults['mesa_dir'],0)
        
        self.crlibm_lib, _ = pym.loadMod("math")
        self.crlibm_lib.math_init()
        
        self.colors_lib,self.colors_def = pym.loadMod("colors")        
        self.colors_lib.colors_init(1,np.array(['lcb98cor.dat']),11, 0)

    def __del__(self):
        if 'const_lib' in self.__dict__:
            self.const_lib.colors_shutdown()
            
    def get_bc(self,bandpass,logT,logg,MdivH):
        return self.colors_lib.get_bc_by_name(bandpass, logT, logg, MdivH, 0)