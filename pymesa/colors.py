import pymesa.pyMesaUtils as pym
import numpy as np

from . import const
from . import math
from . import chem

class colors(object):
    def __init__(self, defaults):
        self.defaults = defaults
        self.const = const.const(defaults)
        self._strlen = self.const.const_def.strlen

        self.math = math.math(defaults)
        
        self.chem = chem.chem(defaults)

        self.colors_lib,self.colors_def = pym.loadMod("colors",defaults)        
        self.colors_lib.colors_init(defaults['num_files'],defaults['fnames'],defaults['num_colors'], 0)

    def __del__(self):
        if 'colors_lib' in self.__dict__:
            self.colors_lib.colors_shutdown()
            
    def get_bc(self,bandpass,logT,logg,MdivH):
        res = self.colors_lib.get_bc_by_name(bandpass, logT, logg, MdivH, 0)
        pym.error_check(res)
        return res.result

    def get_abs_bolo_mag(self, lum):
        res = self.colors_lib.get_abs_bolometric_mag(lum)
        return res.result

    def get_abs_mag(self,bandpass,logT,logg,MdivH,lum):
        res = self.colors_lib.get_abs_mag_by_name(bandpass, logT, logg, MdivH, lum, 0)
        pym.error_check(res)
        return res.result

    def get_lum(self,bandpass,logT,logg,MdivH,lum):
        res = self.colors_lib.get_lum_band_by_name(bandpass, logT, logg, MdivH, lum,0)
        pym.error_check(res)
        return res.result

    def available_names(self):
        names = np.empty(np.sum(self.defaults['num_colors']),dtype='|S'+str(self._strlen))
        res = self.colors_lib.get_all_bc_names(names,0)
        pym.error_check(res)
        return res.args['names']

    def mdivh(self, composition, zfrac_choice='GS98'):

        res = self.chem.basic_composition_info(composition)

        return self.chem.m_div_h(res['xh'], res['z'], zfrac_choice)