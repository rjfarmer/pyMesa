# Tool to build mesa with python support

# Copyright (C) 2020  Robert Farmer <r.j.farmer@uva.nl>

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
import urllib
import hashlib
import zipfile
import tarfile
import io
import svn.remote
import pathlib

MIN_VERSION = 12780

class mesa(object):
    def __init__(self,MESA_DIR=None,MESASDK_ROOT=None,nonsdk=False):
        self.MESA_DIR = self._get_var(MESA_DIR,'MESA_DIR')
        self.nonsdk = nonsdk
        if not self.nonsdk:
            self.MESASDK_ROOT = self._get_var(MESASDK_ROOT,'MESASDK_ROOT')
        else:
            self.MESASDK_ROOT = None
        self.LIB_EXT = self._platform_check()
        
        self._checkcrpath()
        self.setOMPThreads()
        
        
    def _get_var(self,var,name):
        if var is None:
            if name in os.environ:
                return os.environ.get(name)
            else:
                raise ValueError("Must set "+str(name)+" environment variable or pass as an argument")
        else:
            os.environ[name] = var
            return var
            
        
    def set_paths(self):
        self.DATA_DIR = os.path.join(self.MESA_DIR,'data')
        self.LIB_DIR = os.path.join(self.MESA_DIR,'lib')
        self.INCLUDE_DIR = os.path.join(self.MESA_DIR,'include')

        self.RATES_DATA=os.path.join(self.DATA_DIR,'rates_data')
        self.EOSDT_DATA=os.path.join(self.DATA_DIR,'eosDT_data')
        self.EOSPT_DATA=os.path.join(self.DATA_DIR,'eosPT_data')
        self.ION_DATA=os.path.join(self.DATA_DIR,'ionization_data')
        self.KAP_DATA=os.path.join(self.DATA_DIR,'kap_data')
        self.NET_DATA=os.path.join(self.DATA_DIR,'net_data')

        self.RATES_CACHE=os.path.join(self.RATES_DATA,'cache')
        self.EOSDT_CACHE=os.path.join(self.EOSDT_DATA,'cache')
        self.EOSPT_CACHE=os.path.join(self.EOSPT_DATA,'cache')
        self.ION_CACHE=os.path.join(self.ION_DATA,'cache')
        self.KAP_CACHE=os.path.join(self.KAP_DATA,'cache')
        self.NETS=os.path.join(self.NET_DATA,'nets')

    @property
    def MESA_VERSION(self):
        with open(os.path.join(self.DATA_DIR,'version_number'),'r') as f:
            v=f.readline().strip()
            return int(v)
            
    def version_check(self):
        if self.MESA_VERSION < MIN_VER:
            raise ValueError("MESA versions < "+str(MIN_VER)+" not supported")

    def _platform_check(self):
        p=sys.platform.lower()
        if p == "linux" or p == "linux2":
             return 'so'
        else:
            raise Exception("Platform not support "+str(p))
            
    def _isLinux(self):
        return self._platform_check() == 'so'
    
    def check_shared_lib(self):
        # Check we compiled with shared libraries
        if not os.path.exists(os.path.join(self.LIB_DIR,'libstar.' + self.LIB_EXT)):
            raise ValueError("Recompile MESA with USED_SHARED = yes")
            
    def build_shared(self):
        filename = os.path.join(self.MESA_DIR,'utils','makefile_header')
        
        with open(filename,'r') as f:
            lines = f.readlines()
            
        for idx,i in enumerate(lines):
            if 'USE_SHARED =' in i:
                lines[idx] = 'USE_SHARED = YES'
                
        with open(filename,'w') as f:
            f.writelines(lines)
    
    def loadMod(module):
        MODULE_LIB = os.path.join(self.INCLUDE_DIR,module+"_lib.mod")
        MODULE_DEF = os.path.join(self.INCLUDE_DIR,module+"_def.mod")

        if module == 'run_star_support':
             SHARED_LIB = os.path.join(self.LIB_DIR,"librun_star_support." + self.LIB_EXT)
             MODULE_LIB = os.path.join(self.INCLUDE_DIR,"run_star_support.mod")
        elif module =='run_star_extras':
             SHARED_LIB = os.path.join(self.LIB_DIR,"librun_star_extras." + self.LIB_EXT)
             MODULE_LIB = os.path.join(self.INCLUDE_DIR,"run_star_extras.mod")
        else:
            SHARED_LIB = os.path.join(self.LIB_DIR,"lib"+module+"."+self.LIB_EXT)

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
        
        
    def clean(self,folder):
        print(folder)
        self._runCmd('./clean',folder)
 
    def mk(self,folder):
        self._runCmd('./mk',folder)
    
    def rn(self,folder):
        self._runCmd('./rn',folder)
        
    def re(self,folder,photo):
        self._runCmd('./re',folder,str(photo))
        
    def build_and_test(self,folder):
        self._runCmd('./build_and_text',folder)
        
    def export(self,folder):
        self._runCmd(folder,'./export',self._sdk_path)
        
    def _runCmd(self,cmd,folder,args=''):
        if self._sdk_path is not None:
            subprocess.Popen(['source '+self._sdk_path+'; '+cmd+' '+args],shell=True,cwd=folder,executable='/bin/bash')
        else:
            subprocess.Popen([cmd + ' ' + args],shell=True,cwd=folder,executable='/bin/bash')
    
    def buildModule(self,module):
        self.clean(module)
        self.build_and_test(module)
        self.export(module)
        
    def buildTestCase(self,test_case):
        self.clean(test_case)
        self.mk(test_case)

    def rnTestCase(self,test_case):
        self.buildTestCase(test_case)
        self.rn(test_case)

    def _checkcrpath(self):
        res = subprocess.call(["command","-v","chrpath"], stdout=open(os.devnull, 'wb'))
        if res:
            raise ValueError("Please install chrpath")
  
    def _makeBasicRSE(self,filename):
        with open(filename,'w') as f:
            print('module run_star_extras',file=f)
            print('use star_lib',file=f)
            print('use star_def',file=f)
            print('use const_def',file=f)
            print('use math_lib',file=f)
            print('implicit none',file=f)
            print('contains',file=f)
            print('include "standard_run_star_extras.inc"',file=f)
            print('end module run_star_extras',file=f)
  
    def _makeBasicInlist(self,filename):
        with open(filename,'w') as f:
            print('&star_job',file=f)
            print('/',file=f)
            print('&controls',file=f)
            print('/',file=f)
            print('&pgstar',file=f)
            print('/',file=f)
            

    def buildRunStarSupport():
        cwd = os.getcwd()
        os.chdir(os.path.join(MESA_DIR,'star','make'))
        try:
            compile_cmd = ['gfortran -Wno-uninitialized -fno-range-check',
                          '-fPIC -shared -fprotect-parens',
                          '-fno-sign-zero -fbacktrace -ggdb',
                          '-fopenmp  -std=f2008 -Wno-error=tabs -I../public',
                          '-I../private -I../../include',
                          '-I'+os.path.join(self.MESASDK_ROOT,'include'),
                          '-Wunused-value -W -Wno-compare-reals',
                          '-Wno-unused-parameter -fimplicit-none  -O2',
                          '-ffree-form -x f95-cpp-input -I../defaults',
                          '-I../job -I../other ../job/run_star_support.f90',
                          '-Wl,-rpath=' + self.LIB_DIR,
                          '-o librun_star_support.' + self.LIB_EXT,
                          '-L' + self.LIB_DIR,
                          '-lstar -lgyre -lionization -latm -lcolors -lnet -leos',
                          '-lkap -lrates -lneu -lchem -linterp_2d -linterp_1d',
                          '-lnum -lmtx -lconst -lutils -lrun_star_extras']

            #print(" ".join(compile_cmd))
            x = subprocess.call(" ".join(compile_cmd),shell=True, stdout=open(os.devnull, 'wb'))
            if x:
                raise ValueError("Build run_star_support failed")
            shutil.copy2("librun_star_support."+LIB_EXT,os.path.join(self.LIB_DIR,"librun_star_support." + self.LIB_EXT))
            shutil.copy2('run_star_support.mod',os.path.join(self.INCLUDE_DIR,'run_star_support.mod'))
        except:
            raise
        finally:
            os.chdir(cwd)

        self._runcrpath("librun_star_support." + self.LIB_EXT)


    def buildRunStarExtras(rse=None):
        filename = 'run_star_extras.f'
        output = os.path.join(self.MESA_DIR,'star','make',filename)
        if rse is None:
            self._makeBasicRSE(filename)
        else:
            shutil.copy2(rse,output)

        cwd = os.getcwd()
        os.chdir(os.path.join(self.MESA_DIR,'star','make'))
        try:
            compile_cmd = ['gfortran -Wno-uninitialized -fno-range-check',
                          '-fPIC -shared -fprotect-parens',
                          '-fno-sign-zero -fbacktrace -ggdb',
                          '-fopenmp  -std=f2008 -Wno-error=tabs -I../public',
                          '-I../private -I../../include',
                          '-I'+os.path.join(self.MESASDK_ROOT,'include'),
                          '-Wunused-value -W -Wno-compare-reals',
                          '-Wno-unused-parameter -fimplicit-none  -O2',
                          '-ffree-form -x f95-cpp-input -I../defaults',
                          '-I../job -I../other',
                          filename,
                          '-Wl,-rpath=' + self.LIB_DIR,
                          '-o librun_star_extras.' + self.LIB_EXT,
                          '-L' + self.LIB_DIR,
                          '-lstar -lconst']

            x = subprocess.call(" ".join(compile_cmd),shell=True, stdout=open(os.devnull, 'wb'))
            if x:
                raise ValueError("Build run_star_extras failed")
            shutil.copy2("librun_star_extras." + self.LIB_EXT,os.path.join(self.LIB_DIR,"librun_star_extras." + self.LIB_EXT))
            shutil.copy2('run_star_extras.mod',os.path.join(self.INCLUDE_DIR,'run_star_extras.mod'))
        except:
            raise
        finally:
            os.chdir(cwd)

        self._runcrpath("librun_star_extras." + self.LIB_EXT)
        

    def _runcrpath(self,filename):
        if subprocess.call(["chrpath","-r",str(filename)],shell=True, stdout=open(os.devnull, 'wb'),cwd=self.LIB_DIR):
            raise ValueError("chrpath failed on " + str(filename))  
            

    def setNonSDK(self):
        self.nonsdk = True
        self._sdk_path = None
        shutil.copy2(os.path.join(self.MESA_DIR,'utils','makefile_header_nonsdk'),os.path.join(self.MESA_DIR,'utils','makefile_header'))
        
    def activateSDK(self):
        self.MESASDK_ROOT = os.path.realpath(self.MESASDK_ROOT)
        os.environ['MESASDK_ROOT'] = self.MESASDK_ROOT
        if self.MESASDK_ROOT is not None:
            self._sdk_path = os.path.join(self.MESASDK_ROOT,'bin','mesasdk_init.sh')
        else:
            raise ValueError("Must set MESASDK_ROOT first")
            
        subprocess.Popen('source '+self._sdk_path, shell=True, executable="/bin/bash")

        
                        
    def downloadZip(self,version=-1):
        data = self._getMesaData()
        if version == -1:
            version = self.getLatestVersion()
        
        return self._download(data[version],self.MESA_DIR)
        
        
    def downloadSVN(self,version=None):
        mesa_svn = 'https://subversion.assembla.com/svn/mesa%5Emesa/trunk'
        if version == -1:
            version = self.getLatestVersion()
            
        print("Checking out "+ str(version))
        r = svn.remote.RemoteClient(mesa_svn)
        r.checkout(self.MESA_DIR,version)
        
        return self.MESA_DIR
        
    def downloadGit(self,version=-1):
        pass
        
    def downloadSDK(self,version=-1):
        data = self._getSDKdata()
        if version == -1:
            version = self.getLatestSDKVersion()
        
        return self._download(data[version],self.MESASDK_ROOT)
        
    def _download(self,data,filename):

        url = data['url']
        fhash = data['hash']
        extension = data['ext']
            
        fileout = urllib.parse.urlparse(url)
        file_out = os.path.basename(fileout.path)
        output = filename+'.'+extension
        self._downloadFile(output,url,fhash)
            
        print("Extracting file")
        self._extractFile(output,output.replace(extension,''))
        
        return output
        
        
    def preinstallSDK(self):
        sdk_path = self.downloadSDK()
        
        self.MESASDK_ROOT = os.realpath(sdk_path)
        os.environ['MESASDK_ROOT'] = os.realpath(sdk_path)
        
    def installSDK(self):
        self.activateSDK()
        
    def postinstallSDK(self):
        pass
        
    def preinstallMesa(self,zip_src=True,version=-1):
        if zip_src:
            mesa_path = self.downloadZip(version=version)
        else:
            os.chdir(os.path.basename(self.MESA_DIR))
            mesa_path = self.downloadSVN(version=version)
        
        self.MESA_DIR = os.path.realpath(mesa_path)
        os.environ['MESA_DIR'] = os.path.realpath(mesa_path)
            
            
    def installMesa(self):
        self.clean(self.MESA_DIR)
        self.build_shared()
        self.mk(self.MESA_DIR)
        
    def postinstallMesa(self):
        pass
        
    def listMesaVersions(self):
        versions = self._getMesaData()
        return list(versions.keys())
        
    def _getMesaData(self):
        return self._readFile(self._mesa_versions_file) 

    def _getSDKdata(self):
        if self._isLinux():
            return self._readFile(self._mesasdk_versions_file)
        else:
            raise ValueError("Platform not supported")

    def getLatestVersion(self):
        return self.listMesaVersions()[0]
  
    def getLatestSDKVersion(self):
        return self.listSDKVersions()[0]

    def listSDKVersions(self):
        if self._isLinux():
            versions = self._getSDKdata()
        else:
            raise ValueError("Platform not supported")
        
        return list(versions.keys())
 
    @property
    def _mesa_versions_file(self):
        return os.path.join(self._getRootFolder(),'mesa_versions.txt')
    
    @property
    def _mesasdk_versions_file(self):
        return os.path.join(self._getRootFolder(),'mesasdk_linux.txt')
                                        
    
    def setOMPThreads(self,num_threads=-1):
        if num_threads < 0:
            num_threads = os.cpu_count()
        
        os.environ['OMP_NUM_THREADS'] = str(num_threads)
            
    def installLatest(self):
        self.preinstallSDK()
        self.installSDK()
        self.postinstallSDK()
        
        self.preinstallMesa()
        self.installMesa()
        self.postInstallMesa()
        
        
    def buildRun(self,folder):
        self.activateSDK()
        os.chdir(folder)
        self.clean()
        self.mk()
        self.rn()
        
    def _readFile(self,filename):
        res = {}
        with open(filename,'r') as f:
            lines = f.readlines()
        
        for l in lines:
            version, url, ext, fhash = l.split()
            res[str(version)] = {'url':url,'hash':fhash,'ext':ext}
        
        return res
        
    def _downloadFile(self,filename,url,fhash):
        print("Downloading ",url)
        
        resp = urllib.request.urlopen(url)
        length = resp.getheader('content-length')
        blocksize = 1024
        if length:
            length = int(length)
        else:
            length = 100000

        with open(filename,'wb') as f:
            size = 0
            while True:
                buff = resp.read(blocksize)
                if not buff:
                    break
                f.write(buff)
                size += len(buff)
                if length:
                    print('Done {:.2f}%\r'.format((size/length)*100), end='')
            print()
                
        if not self._checkHash(filename, fhash):
            raise
        
        
    def _extractFile(self, file_in, fold_out):
        if file_in.endswith('.zip'):
            extract_f = zipfile.ZipFile
        elif file_in.endswith('.tar.gz'):
            extract_f = tarfile.open
        else:
            raise ValueError("Filetype not supported")
            
        with extract_f(file_in, 'r') as f:
            f.extractall(os.path.dirname(fold_out))

    def _checkHash(self, filename, fhash):
        if fhash.startswith('md5:'):
            file_hash = self._md5(filename)
            if file_hash != fhash.replace('md5:',''):
                os.remove(filename)
                raise ValueError("File corrupted in download try again")
            else:
                return True
        else:
            raise ValueError("Hash type not supported")
            
        return False
        
 
    def _md5(self,filename):
        hash_md5 = hashlib.md5()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
        
    def _getRootFolder(self):
        return os.path.abspath(os.path.dirname(__file__))
        
        
    def listTestCases(self):
        return [p.name for p in pathlib.Path(os.path.join(self.MESA_DIR,'star','test_suite')).iterdir()]

    @property
    def defaults(self):
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
        defaults['mesa_dir'] = self.MESA_DIR

        # Eos
        defaults['eos_file_prefix'] = 'mesa'
        defaults['eosDT_cache_dir'] = ''
        defaults['eosPT_cache_dir'] = ''
        defaults['eosDE_cache_dir'] = ''
        defaults['eos_use_cache'] = True

        # Ion
        defaults['file_prefix'] = 'ion'
        defaults['Z1_suffix'] = ''
        defaults['ionization_cache_dir'] = self.ION_CACHE
        defaults['ion_use_cache'] = True

        # Kap
        defaults['kap_file_prefix'] = 'gs98'
        defaults['CO_prefixdefaults'] = 'gs98_co'
        defaults['lowT_prefix'] = 'lowT_fa05_gs98'
        defaults['blend_logT_upper_bdy'] = 3.88
        defaults['blend_logT_lower_bdy'] = 3.80
        defaults['kap_use_cache'] = True
        defaults['kap_cache_dir'] = self.KAP_CACHE
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

        return defaults

        
class MesaError(Exception):
    pass


        


    
    
    
    

