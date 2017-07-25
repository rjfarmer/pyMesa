import gfort2py as gf
import numpy as np
import os

MESA_DIR = os.environ.get('MESA_DIR')

LIB_DIR = os.path.join(MESA_DIR,'lib')
INCLUDE_DIR = os.path.join(MESA_DIR,'include')

FOLDER = "const"

SHARED_LIB = os.path.join(LIB_DIR,"lib"+FOLDER+".so")
MODULE = os.path.join(INCLUDE_DIR,FOLDER+"_lib.mod")  

#Currenly broken while i try to parse what number format 0.477d1a894a74e4@-1 is

x=gf.fFort(SHARED_LIB,MODULE,reload=True)


