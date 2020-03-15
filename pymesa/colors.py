import pymesa.pyMesaUtils as pym
import numpy as np

from . import const
from . import math

class colors(object):
    def __init__(self, defaults):
        self.const = const.const(defaults)
        self.math = math.math(defaults)
        
        self.colors_lib,self.colors_def = pym.loadMod("colors",defaults)        
        self.colors_lib.colors_init(defaults['num_files'],defaults['fnames'],defaults['num_colors'], 0)

    def __del__(self):
        if 'colors_lib' in self.__dict__:
            self.colors_lib.colors_shutdown()
            
    def get_bc(self,bandpass,logT,logg,MdivH):
        res = self.colors_lib.get_bc_by_name(bandpass, logT, logg, MdivH, 0)
        pym.error_check(res)
        return res
