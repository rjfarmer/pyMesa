import pymesa.pyMesaUtils as pym


class const(object):
    def __init__(self):
        self.const_lib, self.const_def = pym.loadMod("const")

