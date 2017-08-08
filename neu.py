
import gfort2py as gf
import numpy as np
import os

MESA_DIR = os.environ.get('MESA_DIR')

LIB_DIR = os.path.join(MESA_DIR,'lib')
INCLUDE_DIR = os.path.join(MESA_DIR,'include')

FOLDER = "neu"

SHARED_LIB = os.path.join(LIB_DIR,"lib"+FOLDER+".so")
MODULE = os.path.join(INCLUDE_DIR,FOLDER+"_lib.mod")  

x=gf.fFort(SHARED_LIB,MODULE,rerun=True)

num_neu_types=5
num_neu_rvs=5

flags=np.zeros(num_neu_types)
flags[:]=True

sources=np.zeros((num_neu_types,num_neu_rvs))
info=0
x.neu_get(10**9,9.0,10**7.0,7.0,1.0,1.0,1.0,7.5,flags,sources,info)
