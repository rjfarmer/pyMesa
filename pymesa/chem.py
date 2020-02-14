import pymesa.pyMesaUtils as pym
import numpy as np

class chem(object):
    def __init__(self, defaults=pym.defaults):
        self.const_lib, self.const_def = pym.loadMod("const")
        self.const_lib.const_init(defaults['mesa_dir'],0)
        
        self.crlibm_lib, _ = pym.loadMod("math")
        self.crlibm_lib.math_init()
        
        self.chem_lib,self.chem_def = pym.loadMod("chem")
        self.chem_lib.chem_init(defaults['isotopes_filename'],0)
        
        self._choices = {'AG89':self.chem_def.AG89_zfracs,
                       'GN93':self.chem_def.GN93_zfracs,
                       'GS98':self.chem_def.GS98_zfracs,
                       'L03':self.chem_def.L03_zfracs,
                       'AGS05':self.chem_def.AGS05_zfracs,
                       'AGSS09':self.chem_def.AGSS09_zfracs,
                       'L09':self.chem_def.L09_zfracs,
                       'A09':self.chem_def.A09_Prz_zfracs
                    }

    def __del__(self):
        if 'chem_lib' in self.__dict__:
            self.chem_lib.chem_shutdown()
            
    def basic_composition_info(self,isotopes):
        """
            Given dict of isotopes and their abundances:
                {'h1':0.25,'he4':0.25,'c12':0.25,'o16':0.25}
            
            Return things like abar,zbar etc
        """
        
        num_isos = len(isotopes)
        chem_ids = np.zeros(num_isos)
        x = np.zeros(num_isos)
        
        j=0
        for k,v in isotopes.items():
           c = self.chem_lib.chem_get_iso_id(k)
           if c <= 0:
               raise ValueError("Bad chem id "+str(k)+" got "+str(c))
           chem_ids[j] = c
           x[j] = v
           j = j+1
        
        res = self.chem_lib.basic_composition_info(num_isos, chem_ids, x,
                0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0)
        
        return res
        
    def zfrac_choices(self):
        return list(self._choices.keys())
        
    def m_div_h(self, x, z, zfrac_choice='GS98'):
        
        if not zfrac_choice in self._choices:
            raise ValueError("zfrac choice not valid")
            
        zc = self._choices[zfrac_choice]
        
        return self.chem_lib.chem_M_div_h(x,z,zc)
        
        