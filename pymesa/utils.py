import pymesa.pyMesaUtils as pym

from . import const
from . import math

class utils(object):
    def __init__(self, defaults):
        self.const = const.const(defaults)
        self.math = math.math(defaults)
        
        self.utils_lib, self.utils_def = pym.loadMod("utils",defaults)
