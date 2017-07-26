import gfort2py as gf
import numpy as np
import os

MESA_DIR = os.environ.get('MESA_DIR')

LIB_DIR = os.path.join(MESA_DIR,'lib')
INCLUDE_DIR = os.path.join(MESA_DIR,'include')

FOLDER = "colors"

SHARED_LIB = os.path.join(LIB_DIR,"lib"+FOLDER+".so")
MODULE = os.path.join(INCLUDE_DIR,FOLDER+"_lib.mod")  

x=gf.fFort(SHARED_LIB,MODULE,reload=True)
