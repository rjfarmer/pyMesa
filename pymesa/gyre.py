import pymesa.pyMesaUtils as pym
import numpy as np

class gyre(object):
    def __init__(self, namelist, defaults):
        self.gyre_lib, _ = pym.loadMod("gyre",defaults)
        self.namelist = namelist
        self.gyre_lib.gyre_init(namelist)

    def read_model(self, filename):
        self.gyre_lib.gyre_read_model(filename)
