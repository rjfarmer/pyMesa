import pymesa.pyMesaUtils as pym
import os
import numpy as np

from . import const
from . import math
from . import chem
from . import atm
from . import ion
from . import eos
from . import kap
from . import rates

class net(object):
    def __init__(self, defaults):
        self.defaults = defaults
        self.const = const.const(defaults)
        self.math = math.math(defaults)
        self.chem = chem.chem(defaults)
        self.atm = atm.atm(defaults)
        self.ion = ion.ion(defaults)
        self.eos = eos.eos(defaults)
        self.kap = kap.kap(defaults)
        self.rates = rates.rates(defaults)
    
        self.net_lib, self.net_def = pym.loadMod("net",defaults)
        self.net_lib.net_init(0)
        self.setup = False
        
        
    def net_setup(self, net_file):
        self.net_file = net_file

        ierr=0
        # Net setup
        self.net_handle = self.net_lib.alloc_net_handle(ierr).result
        self.net_lib.net_start_def(self.net_handle, ierr)
        self.net_lib.read_net_file(self.net_file,self.net_handle, ierr)
        self.net_lib.net_finish_def(self.net_handle, ierr)

        self.net_lib.net_set_logtcut(self.net_handle, -1,-1, ierr)
        self.net_lib.net_set_fe56ec_fake_factor(self.net_handle, 10**-7, 3.0*10**9, ierr)

        self.species = self.net_lib.net_num_isos(self.net_handle, ierr).result
        self.num_reactions =  self.net_lib.net_num_reactions(self.net_handle, ierr).result

        rates_reaction_id_max = self.rates.rates_def.rates_reaction_id_max

        which_rates = np.zeros(self.rates.rates_def.rates_reaction_id_max)
        reaction_id = np.zeros(self.num_reactions)
        which_rates[:] = self.rates.rates_def.rates_jr_if_available
        self.net_lib.net_set_which_rates(self.net_handle, which_rates, ierr)
        self.net_lib.net_setup_tables(self.net_handle, '', ierr)
        
                
        num_chem_isos = self.chem.chem_def.num_chem_isos
        
        chem_id = np.zeros(num_chem_isos)
        net_iso_table = np.zeros(num_chem_isos)
        reaction_id = np.zeros(self.num_reactions)
        
        res = self.net_lib.get_chem_id_table(self.net_handle, self.species, chem_id, ierr)
        chem_id = res.args['chem_id']
        
        
        res = self.net_lib.get_net_iso_table(self.net_handle, net_iso_table, ierr)
        net_iso = res.args['net_iso_table']
        
        
        res = self.net_lib.get_reaction_id_table(self.net_handle, self.num_reactions, reaction_id, ierr)
        reaction_id = res.args['reaction_id']
         
        reaction_table = np.zeros(rates_reaction_id_max)        
        res = self.net_lib.get_net_reaction_table(self.net_handle, reaction_table, ierr)
        
        reaction_table = res.args['net_reaction_table']
        
        #Setup reaction energies
        allQ = self.rates.rates_def.std_reaction_qs
        allQneu = self.rates.rates_def.std_reaction_neuqs
        
        self.reaction_Qs  = np.zeros(self.num_reactions) 
        self.reaction_neuQs = np.zeros(self.num_reactions) 
        
        
        for i in range(self.num_reactions):
            self.reaction_Qs[i] = allQ[reaction_id[i]]
            self.reaction_neuQs[i] = allQneu[reaction_id[i]]
        
                
        self.lwork = self.net_lib.net_work_size(self.net_handle, ierr).result

        self.work = np.zeros(self.lwork)
        
        self.setup = True
            
            
    def get_net_info(self):
        pass

    def get_net_general_info(self):
        if not self.setup:
            raise ValueError("Call net_setup first") 
        g = {}
        res = self.net_lib.net_ptr(self.net_handle, g, 0)
        pym.error_check(res)
        return res.args['g']
        

    @property
    def rate_factors(self):
        x = np.zeros(self.num_reactions)
        x[:] = 1
        return x


    def net_get(self, composition, temp, rho, just_dxdt=False, weak_rate_factor=1,
                screening_mode='chugunov',theta_e_for_graboske_et_al=0):
        
        comp = self.chem.basic_composition_info(composition)
        
        X = comp['xh']
        Z = comp['z']
        abar = comp['abar']
        zbar = comp['zbar']
        z2bar = comp['z2bar']
        ye = comp['ye']
        species = len(composition)
        chem_id, xa = self.chem.chem_ids(composition)
        log10Rho = self.const.const_def.arg_not_provided
        log10T = self.const.const_def.arg_not_provided
        z53bar = comp['z53bar']

        n = {}

        log10Rho = np.log10(rho)
        log10T = np.log10(temp)
        eta, d_eta_dlnT, d_eta_dlnRho = (0,0,0) # Should compute these somehow
        
        
        screening_mode = self.rates.which_screening(screening_mode)

        num_isos = species
        dxdt = np.zeros(num_isos)
        d_eps_nuc_dx = np.zeros(num_isos)
        d_dxdt_dRho = np.zeros(num_isos)
        d_dxdt_dT = np.zeros(num_isos)
        d_dxdt_dx = np.zeros((num_isos, num_isos))
        eps_nuc_categories = np.zeros(self.chem.chem_def.num_categories)
        

        result = self.net_lib.net_get(self.net_handle, just_dxdt, n,
                                    self.species, self.num_reactions,
                                    xa, temp, log10T, rho, log10Rho,
                                    abar, zbar, z2bar, ye,
                                    eta, d_eta_dlnT, d_eta_dlnRho,
                                    self.rate_factors, weak_rate_factor,
                                    self.reaction_Qs, self.reaction_neuQs,
                                    False, False,
                                    0,0,0,d_eps_nuc_dx,
                                    dxdt, d_dxdt_dRho, d_dxdt_dT, d_dxdt_dx,
                                    screening_mode,theta_e_for_graboske_et_al,
                                    eps_nuc_categories,0.0,
                                    self.lwork, self.work, 0 
                                    )

        return result



