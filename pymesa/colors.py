import pymesa.pyMesaUtils as pym

class colors(object):
    def __init__(self):
        self.col_lib,self.col_def = pym.loadMod("colors")
