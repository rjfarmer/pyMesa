# Tool to build mesa with python support

# Copyright (C) 2017  Robert Farmer <r.j.farmer@uva.nl>

#This file is part of pyMesa.

#pyMesa is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 2 of the License, or
#(at your option) any later version.

#pyMesa is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with pyMesa. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import gfort2py as gf
import numpy as np
import os
import sys
import shutil
import subprocess


#MESA DIR check and path set
if "MESA_DIR" not in os.environ:
    raise ValueError("Must set MESA_DIR environment variable")
else:
    MESA_DIR = os.environ.get('MESA_DIR')


DATA_DIR = os.path.join(MESA_DIR,'data')
LIB_DIR = os.path.join(MESA_DIR,'lib')
INCLUDE_DIR = os.path.join(MESA_DIR,'include')

RATES_DATA=os.path.join(DATA_DIR,'rates_data')
EOSDT_DATA=os.path.join(DATA_DIR,'eosDT_data')
EOSPT_DATA=os.path.join(DATA_DIR,'eosPT_data')
ION_DATA=os.path.join(DATA_DIR,'ionization_data')
KAP_DATA=os.path.join(DATA_DIR,'kap_data')

NET_DATA=os.path.join(DATA_DIR,'net_data')

RATES_CACHE=os.path.join(RATES_DATA,'cache')
EOSDT_CACHE=os.path.join(EOSDT_DATA,'cache')
EOSPT_CACHE=os.path.join(EOSPT_DATA,'cache')
ION_CACHE=os.path.join(ION_DATA,'cache')
KAP_CACHE=os.path.join(KAP_DATA,'cache')
NETS=os.path.join(NET_DATA,'nets')

MESASDK_ROOT=os.path.expandvars('$MESASDK_ROOT')

with open(os.path.join(DATA_DIR,'version_number'),'r') as f:
    v=f.readline().strip()
    MESA_VERSION=int(v)

if MESA_VERSION < 12708:
    raise ValueError("MESA versions < 12708 not supported")

p=sys.platform.lower()

if p == "linux" or p == "linux2":
    LIB_EXT='so'
else:
    raise Exception("Platform not support "+str(p))
    
    
# Check we compiled with shared libraries
if not os.path.exists(os.path.join(LIB_DIR,'libstar.'+LIB_EXT)):
    raise ValueError("Recompile MESA with USED_SHARED = yes")
    
    

def loadMod(module):
    MODULE_LIB = os.path.join(INCLUDE_DIR,module+"_lib.mod")
    MODULE_DEF = os.path.join(INCLUDE_DIR,module+"_def.mod")

    if module =='crlibm':
        SHARED_LIB = os.path.join(LIB_DIR,"libf2crlibm."+LIB_EXT)
    elif module =='run_star_support':
         SHARED_LIB = os.path.join(LIB_DIR,"librun_star_support."+LIB_EXT)
         MODULE_LIB = os.path.join(INCLUDE_DIR,"run_star_support.mod")
    elif module =='run_star_extras':
         SHARED_LIB = os.path.join(LIB_DIR,"librun_star_extras."+LIB_EXT)
         MODULE_LIB = os.path.join(INCLUDE_DIR,"run_star_extras.mod")
    else:
        SHARED_LIB = os.path.join(LIB_DIR,"lib"+module+"."+LIB_EXT)

    x = None
    y = None

    try:
        x = gf.fFort(SHARED_LIB,MODULE_LIB,rerun=True)
    except FileNotFoundError:
        pass

    try:
        y = gf.fFort(SHARED_LIB,MODULE_DEF,rerun=True)
    except FileNotFoundError:
        pass

    return x, y


def buildModule(module):
    cwd = os.getcwd()
    os.chdir(os.path.join(MESA_DIR,module))

    try:
        x=subprocess.call("./clean >/dev/null 2>/dev/null",shell=True)
        if x:
            raise ValueError("clean failed")
        x = subprocess.call("./build_and_test >/dev/null 2>/dev/null",shell=True)
        if x:
            raise ValueError("Build_and_test failed")
        x = subprocess.call("./export >/dev/null 2>/dev/null",shell=True)
        if x:
            raise ValueError("export failed")
    except:
        raise
    finally:
        os.chdir(cwd)

    if MESA_VERSION < 11035:
        os.chdir(LIB_DIR)
        checkcrpath()
        try:
            x = subprocess.call("chrpath -r lib"+module+"."+LIB_EXT,shell=True)
            if x:
                raise ValueError("chrpath failed")
        except:
            raise
        finally:
            os.chdir(cwd)

    print("Built "+str(module))

def buildRunStarSupport():
    cwd = os.getcwd()
    os.chdir(os.path.join(MESA_DIR,'star','make'))
    try:
        compile_cmd = ['gfortran -Wno-uninitialized -fno-range-check',
                      '-fPIC -shared -fprotect-parens',
                      '-fno-sign-zero -fbacktrace -ggdb',
                      '-fopenmp  -std=f2008 -Wno-error=tabs -I../public',
                      '-I../private -I../../include',
                      '-I'+os.path.join(MESASDK_ROOT,'include'),
                      '-Wunused-value -W -Wno-compare-reals',
                      '-Wno-unused-parameter -fimplicit-none  -O2',
                      '-ffree-form -x f95-cpp-input -I../defaults',
                      '-I../job -I../other ../job/run_star_support.f90',
                      '-Wl,-rpath=' + LIB_DIR,
                      '-o librun_star_support.'+LIB_EXT,
                      '-L'+LIB_DIR,
                      '-lstar -lgyre -lionization -latm -lcolors -lnet -leos',
                      '-lkap -lrates -lneu -lchem -linterp_2d -linterp_1d',
                      '-lnum -lmtx -lconst -lutils -lrun_star_extras']
        if MESA_VERSION < 12202:
            compile_cmd.append('-lf2crlibm -lcrlibm')

        print(" ".join(compile_cmd))
        x = subprocess.call(" ".join(compile_cmd),shell=True, stdout=open(os.devnull, 'wb'))
        if x:
            raise ValueError("Build run_star_support failed")
        shutil.copy2("librun_star_support."+LIB_EXT,os.path.join(LIB_DIR,"librun_star_support."+LIB_EXT))
        shutil.copy2('run_star_support.mod',os.path.join(INCLUDE_DIR,'run_star_support.mod'))
    except:
        raise
    finally:
        os.chdir(cwd)

    os.chdir(LIB_DIR)
    checkcrpath()
    try:
        x = subprocess.call("chrpath -r librun_star_support."+LIB_EXT,shell=True, stdout=open(os.devnull, 'wb'))
        if x:
            raise ValueError("chrpath failed")
    except:
        raise
    finally:
        os.chdir(cwd)

    print("Built run_star_support")


def buildRunStarExtras(rse=None):
    filename = 'run_star_extras.f'
    output = os.path.join(MESA_DIR,'star','make',filename)
    if rse is None:
        with open(output,'w') as f:
            print('module run_star_extras',file=f)
            print('use star_lib',file=f)
            print('use star_def',file=f)
            print('use const_def',file=f)
            if MESA_VERSION < 12202:
                print('use crlibm_lib',file=f)
            print('implicit none',file=f)
            print('contains',file=f)
            print('include "standard_run_star_extras.inc"',file=f)
            print('end module run_star_extras',file=f)
    else:
        shutil.copy2(rse,output)

    cwd = os.getcwd()
    os.chdir(os.path.join(MESA_DIR,'star','make'))
    try:
        compile_cmd = ['gfortran -Wno-uninitialized -fno-range-check',
                      '-fPIC -shared -fprotect-parens',
                      '-fno-sign-zero -fbacktrace -ggdb',
                      '-fopenmp  -std=f2008 -Wno-error=tabs -I../public',
                      '-I../private -I../../include',
                      '-I'+os.path.join(MESASDK_ROOT,'include'),
                      '-Wunused-value -W -Wno-compare-reals',
                      '-Wno-unused-parameter -fimplicit-none  -O2',
                      '-ffree-form -x f95-cpp-input -I../defaults',
                      '-I../job -I../other',
                      filename,
                      '-Wl,-rpath=' + LIB_DIR,
                      '-o librun_star_extras.'+LIB_EXT,
                      '-L'+LIB_DIR,
                      '-lstar -lconst']
        if MESA_VERSION < 12202:
            compile_cmd.append('-lf2crlibm -lcrlibm')

        print(" ".join(compile_cmd))
        x = subprocess.call(" ".join(compile_cmd),shell=True, stdout=open(os.devnull, 'wb'))
        if x:
            raise ValueError("Build run_star_extras failed")
        shutil.copy2("librun_star_extras."+LIB_EXT,os.path.join(LIB_DIR,"librun_star_extras."+LIB_EXT))
        shutil.copy2('run_star_extras.mod',os.path.join(INCLUDE_DIR,'run_star_extras.mod'))
    except:
        raise
    finally:
        os.chdir(cwd)

    os.chdir(LIB_DIR)
    checkcrpath()
    try:
        x = subprocess.call("chrpath -r librun_star_extras."+LIB_EXT,shell=True, stdout=open(os.devnull, 'wb'))
        if x:
            raise ValueError("chrpath failed")
    except:
        raise
    finally:
        os.chdir(cwd)

    print("Built run_star_extras")

class MesaError(Exception):
    pass


def checkcrpath():
    res = subprocess.call(["command","-v","chrpath"], stdout=open(os.devnull, 'wb'))
    if res:
        raise ValueError("Please install chrpath")


def make_basic_inlist():
    with open('inlist','w') as f:
        print('&star_job',file=f)
        print('/',file=f)
        print('&controls',file=f)
        print('/',file=f)
        print('&pgstar',file=f)
        print('/',file=f)
        


defaults = {}

# Atm
defaults['atm_use_cache'] = True

# Chem
defaults['isotopes_filename'] = 'isotopes.data'

# Colors
defaults['num_files'] = 1
defaults['fnames'] = np.array(['lcb98cor.dat'])
defaults['num_colors'] = 11

# Const
defaults['mesa_dir'] = MESA_DIR

# Eos
defaults['eos_file_prefix'] = 'mesa'
defaults['eosDT_cache_dir'] = ''
defaults['eosPT_cache_dir'] = ''
defaults['eosDE_cache_dir'] = ''
defaults['eos_use_cache'] = True

# Ion
defaults['file_prefix'] = 'ion'
defaults['Z1_suffix'] = ''
defaults['ionization_cache_dir'] = ION_CACHE
defaults['ion_use_cache'] = True

# Kap
defaults['kap_file_prefix'] = 'gs98'
defaults['CO_prefixdefaults'] = 'gs98_co'
defaults['lowT_prefix'] = 'lowT_fa05_gs98'
defaults['blend_logT_upper_bdy'] = 3.88
defaults['blend_logT_lower_bdy'] = 3.80
defaults['kap_use_cache'] = True
defaults['kap_cache_dir'] = KAP_CACHE
defaults['kap_config_file'] = ''
defaults['kap_show_info'] = False

# Net
# Nothing

# Neu
# Nothing

# Rates
defaults['reactionlist_filename'] = 'reactions.list'
defaults['jina_reaclib_filename'] = 'jina_reaclib_results_20130213default2'
defaults['rates_table_dir_in'] = 'rate_tables'
defaults['use_suzuki_weak_rates'] = False
defaults['use_special_weak_rates'] = False
defaults['special_weak_states_file'] = ''
defaults['special_weak_transitions_file'] = ''
defaults['rates_cache_dir'] = ''
    
    
    
    

