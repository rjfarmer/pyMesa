import pyMesa as pym
import numpy as np
import os
import tempfile

class pyStar(object):
    def __init__(self, rse = None):
        self.star_lib, self.star_def = pym.loadMod("star")
        
        self.rse, _ = pym.loadMod('run_star_extras')
        self.star, _ = pym.loadMod("run_star_support")

        self.just_did_backup = False
        self.first_try = True
        self.continue_evolve_loop = True

        self.star_id = 0
        self.inlist = 'inlist'

        self.controls = {}
        self.star_job = {}
        self._to_be_added_ctrls = {}
      
        self.hist_names = []
        self.prof_names = []  
        self.hist_data = []
        self.prof_data = []
        

    def error_check(self, res):
        if isinstance(res,dict) and 'ierr' in res:
            if res['ierr'] is not 0:
                raise pym.MesaError('Non zero ierr='+str(res['ierr']))
        else:
            if int(res) != 0:
                raise pym.MesaError('Non zero ierr='+str(res))

    def new_star(self, inlist='inlist'):
        res = self.star_lib.alloc_star(self.star_id,0)
        self.error_check(res)
        self.star_id = res['id']
        if self.star_id <= 0:
            raise ValueError("New star init failed")
        self.inlist = inlist
        res = self.star.read_star_job_id(self.star_id, self.inlist, 0)
        self.error_check(res)
        res = self.star.star_setup(self.star_id, self.inlist, 0)
        self.error_check(res)

    def before_evolve_loop(self):
        res = self.star.before_evolve_loop(False,True,False,
                self.star.null_binary_controls,self.rse.extras_controls,
                0,self.inlist,'restart_photo',True,0,self.star_id,0)
        self.error_check(res)

    def single_step(self):
        res = self.star.star_evolve_step(self.star_id, self.first_try, self.just_did_backup)
        return self.check_step(res)

    def model_number(self):
        mod_num = self.star_lib.get_model_number(self.star_id, 0)
        return mod_num

    def before_step_loop(self):
        res = self.star.before_step_loop(self.star_id, 0)
        self.error_check(res)

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
        if step_result == self.star_def.backup:
            step_result = self.star_lib.star_do1_backup(self.star_id)
            self.just_did_backup = True
        else:
            self.just_did_backup = False
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
        self.error_check(res)
        res = res['result']

        if res != self.star_def.keep_going:
            if res != self.star_def.terminate:
                self.continue_evolve_loop = False
                raise ValueError("Something went wrong")
            else:
                # Need to check s%result_reason
                res = self.star.terminate_normal_evolve_loop(self.star_id, 0, False, res, 0)
                self.error_check(res)
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
        self.error_check(res)

    def destroy_star(self):
        self.star_lib.free_star(self.star_id, 0)

    def load_inlist(self, inlist='inlist'):
        self.inlist = inlist
        self.load_star_job(self.inlist)
        self.load_controls(self.inlist)

    def load_star_job(self, inlist):
        self.star_lib.read_star_job_id(self.star_id, inlist, 0)
        res = self.star_lib.star_setup(self.star_id, inlist, 0)
        self.error_check(res)

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
        self.error_check(res)
        return res['dt']
        
    def set_dt(self, dt):
        res = self.star.set_dt_next(self.star_id, dt, 0)
        
    def __del__(self):
        self.star.free_star(self.star_id,0)


def basic():
    # Creates an empty inlist
    #pym.make_basic_inlist() # Or have a file in cwd called 'inlist'

    # Init
    s = pyStar()

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

#basic()


def setinlist():
    s = pyStar()
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
    
setinlist()


