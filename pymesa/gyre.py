import pymesa.pyMesaUtils as pym

class gyre(object):
    def __init__(self, namelist):
        self.gyre_lib, _ = pym.loadMod("gyre")
        self.namelist = namelist
        self.gyre_lib.gyre_init(namelist)

