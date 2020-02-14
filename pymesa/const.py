import pymesa.pyMesaUtils as pym


class const(object):
    def __init__(self, defaults=pym.defaults):
        self.const_lib, self.const_def = pym.loadMod("const")
        self.const_lib.const_init(defaults['mesa_dir'],0)
