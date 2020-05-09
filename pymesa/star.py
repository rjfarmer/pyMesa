import pymesa.pyMesaUtils as pym
import numpy as np
import os
import glob
import tempfile
import subprocess
import shutil

class star(object):
    def __init__(self, defaults, rse = None):
        self.defaults = defaults
        
        self.MESA_DIR = os.path.realpath(defaults['mesa_dir'])
        self.MESASDK_ROOT = os.path.realpath(defaults['MESASDK_ROOT'])
        self.LIB_DIR = os.path.realpath(defaults['LIB_DIR'])
        self.INCLUDE_DIR = os.path.realpath(defaults['INCLUDE_DIR'])
        
        self.buildRunStarExtras(rse)
        self.buildRunStarSupport()
        self.star_lib, self.star_def = pym.loadMod("star",defaults)
        
        self.rse, _ = pym.loadMod('run_star_extras',defaults)
        self.star, _ = pym.loadMod("run_star_support",defaults)

        self.just_did_backup = False
        self.first_try = True
        self.continue_evolve_loop = True
        
        if not self.star_def.have_initialized_star_handles:
            self.star_lib.star_init_star_handles()

        self.star_id = 0
        self.inlist = 'inlist'

        self.controls = {}
        self.star_job = {}
        self._to_be_added_ctrls = {}
      
        self.hist_names = []
        self.prof_names = []  
        self.hist_data = []
        self.prof_data = []
        
    def buildRunStarSupport(self):
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
                          '-I../job -I../other ../job/run_star_support.f90',
                          '-Wl,-rpath=' + self.LIB_DIR,
                          '-o librun_star_support.' + self.defaults['LIB_EXT'],
                          '-L' + self.LIB_DIR,
                          '-lstar -lgyre -lionization -latm -lcolors -lnet -leos',
                          '-lkap -lrates -lneu -lchem -linterp_2d -linterp_1d',
                          '-lnum -lmtx -lconst -lutils -lrun_star_extras']

            #print(" ".join(compile_cmd))
            x = subprocess.call(" ".join(compile_cmd),shell=True, stdout=open(os.devnull, 'wb'))
            if x:
                raise ValueError("Build run_star_support failed")
            shutil.copy2("librun_star_support."+self.defaults['LIB_EXT'],os.path.join(self.LIB_DIR,"librun_star_support." + self.defaults['LIB_EXT']))
            shutil.copy2('run_star_support.mod',os.path.join(self.INCLUDE_DIR,'run_star_support.mod'))
        except:
            raise
        finally:
            os.chdir(cwd)

        pym._runcrpath("librun_star_support." + self.defaults['LIB_EXT'],self.defaults['LIB_DIR'])


    def buildRunStarExtras(self,rse=None):
        filename = 'run_star_extras.f90'
        output = os.path.join(self.MESA_DIR,'star','make',filename)
        if rse is None:
            self._makeBasicRSE(output)
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
                          '-o librun_star_extras.' + self.defaults['LIB_EXT'],
                          '-L' + self.LIB_DIR,
                          '-lstar -lconst']

            x = subprocess.call(" ".join(compile_cmd),shell=True, stdout=open(os.devnull, 'wb'))
            if x:
                raise ValueError("Build run_star_extras failed")
            shutil.copy2("librun_star_extras." + self.defaults['LIB_EXT'],os.path.join(self.LIB_DIR,"librun_star_extras." + self.defaults['LIB_EXT']))
            shutil.copy2('run_star_extras.mod',os.path.join(self.INCLUDE_DIR,'run_star_extras.mod'))
        except:
            raise
        finally:
            os.chdir(cwd)

        pym._runcrpath("librun_star_extras." + self.defaults['LIB_EXT'],self.LIB_DIR)
   
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
  
    def makeBasicInlist(self,filename='inlist'):
        with open(filename,'w') as f:
            print('&star_job',file=f)
            print('/',file=f)
            print('&controls',file=f)
            print('/',file=f)
            print('&pgstar',file=f)
            print('/',file=f)
                        
    def new_star(self, inlist='inlist'):
        self.star_id = self.star_lib.star_find_next_star_id().result
        res = self.star_lib.alloc_star(self.star_id,0)
        pym.error_check(res)
        self.star_id = res.args['id']
        if self.star_id <= 0:
            raise ValueError("New star init failed")
        self.inlist = inlist
        res = self.star.read_star_job_id(self.star_id, self.inlist, 0)
        pym.error_check(res)
        res = self.star.star_setup(self.star_id, self.inlist, 0)
        pym.error_check(res)

    def before_evolve_loop(self):
        res = self.star.before_evolve_loop(False,True,False,
                self.star.null_binary_controls,self.rse.extras_controls,
                0,self.inlist,'restart_photo',True,0,self.star_id,0)
        pym.error_check(res)

    def single_step(self):
        res = self.star.star_evolve_step(self.star_id, self.first_try)
        return self.check_step(res)

    def model_number(self):
        mod_num = self.star_lib.get_model_number(self.star_id, 0)
        return mod_num

    def before_step_loop(self):
        res = self.star.before_step_loop(self.star_id, 0)
        pym.error_check(res)

    def star_check_model(self):
        return self.star_lib.star_check_model(self.star_id)

    def star_pick_next_timestep(self):
        return self.star_lib.star_pick_next_timestep(self.star_id)

    def extras_check_model(self):
        return self.star.extras_check_model(self.star_id, 0)

    def check_step(self, step_result):
        keep_going = False
        if step_result == self.star_def.keep_going:
            step_result = self.star_lib.star_check_model(self.star_id)
            if step_result == self.star_def.keep_going:
                step_result = self.rse.extras_check_model(self.star_id)
                if step_result == self.star_def.keep_going:
                    step_result = self.star_lib.star_pick_next_timestep(self.star_id)
                    if step_result == self.star_def.keep_going:
                        keep_going = True

        if keep_going: # End step normally
            return False

        if step_result == self.star_def.redo:
            step_result = self.star_lib.star_prepare_to_redo(self.star_id)
        if step_result == self.star_def.retry:
            step_result = self.star_lib.star_prepare_to_retry(self.star_id)
        if step_result == self.star_def.terminate:
            self.continue_evolve_loop = False
            return False
        self.first_try = False
        return True

    def step(self):
        while self.single_step():
            if not self.continue_evolve_loop:
                return False
        return True

    def single_evolve(self):
        if not self.continue_evolve_loop:
            return False

        result = 0
        res = 0
        self.first_try = True
        self.just_did_backup = False
        self.single_step()

        res = self.star.after_step_loop(self.star_id, self.inlist, False, result, 0)
        pym.error_check(res)
        res = res['result']

        if res != self.star_def.keep_going:
            if res != self.star_def.terminate:
                self.continue_evolve_loop = False
                raise ValueError("Something went wrong")
            else:
                # Need to check s%result_reason
                res = self.star.terminate_normal_evolve_loop(self.star_id, 0, False, res, 0)
                pym.error_check(res)
                self.continue_evolve_loop = False
                return False

        self.save()
        
        self._pysave()
        
        return True
        
    def _pysave(self):
        if len(self.hist_names):
            self.hist_data.append({'model_number':self.model_number()})
            for i in self.hist_names:
                self.hist_data[-1][i] = self.get_hist(i)
        if len(self.prof_names):
            self.prof_data.append({'model_number':self.model_number()})
            for i in self.prof_names:
                self.prof_data[-1][i] = self.get_prof_nz(i)
                

    def save(self):
        self.star.do_saves(self.star_id, 0)

    def evolve(self):
        self.before_evolve_loop()
        while self.single_evolve():
            if not self.continue_evolve_loop:
                return False
        self.after_evolve_loop()

    def after_evolve_loop(self):
        res = self.star.after_evolve_loop(self.star_id, True, 0)
        pym.error_check(res)

    def destroy_star(self):
        self.star_lib.free_star(self.star_id, 0)

    def load_inlist(self, inlist='inlist'):
        self.inlist = inlist
        self.load_star_job(self.inlist)
        self.load_controls(self.inlist)

    def load_star_job(self, inlist):
        self.star_lib.read_star_job_id(self.star_id, inlist, 0)
        res = self.star_lib.star_setup(self.star_id, inlist, 0)
        pym.error_check(res)

    def load_controls(self, inlist):
        self.star_lib.star_read_controls(self.star_id, inlist, 0)

    def get_hist(self, name):
        return self.star_lib.star_get_history_output_by_id(self.star_id, name)

    def nz(self):
        return int(self.get_hist('num_zones'))

    def get_prof(self, name, zone):
        nz = self.nz()
        if zone > nz:
            raise ValueError("Zones out of range")
        return self.star_lib.star_get_profile_output_by_id(self.star_id,name,zone)
        
    def get_prof_nz(self, name):
        nz = self.nz()
        output = np.zeros(nz+1)
        for i in range(1,nz+1):
            output[i] = self.star_lib.star_get_profile_output_by_id(self.star_id,name,i)
        return output


    def dump_controls(self, fname_star, fname_controls):
        self.star_lib.write_star_job_id(self.star_id, fname_star, 0)
        self.star_lib.star_write_controls(self.star_id, fname_controls, 0)

    def parse_inlist(self, fname):
        opts = {}
        with open(fname,'r') as f:
            lines = f.readlines()

        for i in lines[1:-2]:
            line = i.strip().replace(',','').split('=')
            key = line[0].strip()
            value = ''.join(line[1:]).strip() # Handle strings with = in them
            if '"' in value or len(value)==0:
                value = value.replace(" ","")
                t = str
            elif 'T' in value:
                value = True
                t = bool
            elif 'F' in value:
                value = False
                t = bool
            elif '*' in value or value.count('.')>1:
                t = None
                pass # Arrays handle later
            elif value.count('.')==1:
                value = float(value)
                t = float
            else:
                value = int(value)
                t = int
            key = key.lower()
            opts[key] = {'value':value,'type':t}
        return opts

    def read_inlists(self):
        _, fname_star = tempfile.mkstemp()
        _, fname_controls = tempfile.mkstemp()
        self.dump_controls(fname_star,fname_controls)
        self.controls = self.parse_inlist(fname_controls)
        self.star_job = self.parse_inlist(fname_star)
        os.remove(fname_star)
        os.remove(fname_controls)

    def add_control(self, name, value):
        if not len(self.controls):
            self.read_inlists()

        if name not in self.controls:
            raise AttributeError("Not valid control parameter")

        _, fname = tempfile.mkstemp()
        with open(fname,'w') as f:
            print('&controls',file=f)
            for key, value in self._to_be_added_ctrls:
                print(str(name),' = ',self.controls[key]['type'](value),file=f)
            print('/',file=f)
        self.load_controls(fname)
        os.remove(fname)
        self.read_inlists()

    def add_star_job(self, name, value):
        if not len(self.star_job):
            self.read_inlists()

        if name not in self.star_job:
            raise AttributeError("Not valid star_job parameter")

        _, fname = tempfile.mkstemp()
        with open(fname,'w') as f:
            print('&star_job',file=f)
            print(str(name),' = ',self.star_job[name]['type'](value),file=f)
            print('/',file=f)
        self.load_star_job(fname)
        os.remove(fname)
        self.read_inlists()
        
        
    def add_hist(self, name):
        self.hist_names.append(name)
        
    def add_prof(sef, name):
        self.prof_names.append(name)
        
    def get_dt(self):
        res = self.star.get_dt_next(self.star_id, 0, 0)
        pym.error_check(res)
        return res['dt']
        
    def set_dt(self, dt):
        res = self.star.set_dt_next(self.star_id, dt, 0)
        
    def __del__(self):
        if 'star' in self.__dict__:
            self.star.free_star(self.star_id,0)


def basic():
    # Creates an empty inlist
    #pym.make_basic_inlist() # Or have a file in cwd called 'inlist'

    # Init
    s = star()

    # Init new star
    s.new_star()
    s.evolve() # Run till end
    s.get_hist('star_age')
    s.get_prof('dm',1)
    # Might need to ctrl+c to stop the run
    mass=s.get_prof_nz('mass')
    temp=s.get_prof_nz('logT')    
    import matplotlib.pyplot as plt
    plt.plot(mass,temp)
    plt.show()


def singlestepping():
    s = star()
    s.new_star()
    s.before_evolve_loop()
    s.single_evolve() # One step
    print(s.get_hist('star_age'))
    print(s.get_prof('dm',1))
    print(s.get_hist('star_mass'))
    print(s.controls['initial_mass'])
    print(s.get_dt())
    s.set_dt(s.get_dt()/2.0)
    print(s.get_dt())
    s.star.star_set_v_flag(s.star_id, True, 0) # Can call any star_lib function that takes id instead of s
    s.single_evolve() # One step
    s.after_evolve_loop() # End evolution
    

