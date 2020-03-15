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
        
        
        
        
        
        
        
        
        
     
        # self.net_file = net_file

        # init = 0
        # # Net setup
        # self.net_handle=net_lib.alloc_net_handle(ierr)
        # self.net_lib.net_start_def(self.net_handle, ierr)
        # self.net_lib.read_net_file(self.net_file,self.net_handle, ierr)
        # self.net_lib.net_finish_def(self.net_handle, ierr)

        # self.net_lib.net_set_logtcut(self.net_handle, -1,-1, ierr)
        # self.net_lib.net_set_fe56ec_fake_factor(self.net_handle, 10**-7, 3.0*10**9, ierr)

# # Accessing the g pointer is broken
# # g={}
# # res = net_lib.net_ptr(handle, g, ierr)
# # g=res['g'] # Note this is only a copy of the pointer, changes wont propagate back to mesa

        # species = net_lib.net_num_isos(self.net_handle, ierr)
        # num_reactions =  net_lib.net_num_reactions(self.net_handle, ierr)

        # rates_reaction_id_max = rates_def.rates_reaction_id_max.get()

        # which_rates = np.zeros(rates_def.rates_reaction_id_max.get())
        # reaction_id = np.zeros(num_reactions)
        # which_rates[:] = rates_def.rates_jr_if_available.get()
        # #rates_lib.set_which_rates(ierr)
        # self.net_lib.net_set_which_rates(self.net_handle, which_rates, ierr)
        # self.net_lib.net_setup_tables(self.net_handle, '', ierr)

# End net setup


# num_chem_isos = chem_def.num_chem_isos.get()

# chem_id=np.zeros(num_chem_isos)
# net_iso_table=np.zeros(num_chem_isos)
         
# res=net_lib.get_chem_id_table(handle, species, chem_id, ierr)
# chem_id = res['chem_id']

# res=net_lib.get_net_iso_table(handle, net_iso_table, ierr)
# net_iso = res['net_iso_table']

# res=net_lib.get_reaction_id_table(handle, num_reactions, reaction_id, ierr)
# reaction_id = res['reaction_id']
 
# reaction_table=np.zeros(rates_reaction_id_max)        
# res=net_lib.get_net_reaction_table(handle, reaction_table, ierr)

# reaction_table = res['net_reaction_table']

# #Setup reaction energies
# allQ = rates_def.std_reaction_qs.get()
# allQneu = rates_def.std_reaction_neuqs.get()

# reaction_Qs  = np.zeros(num_reactions) 
# reaction_neuQs = np.zeros(num_reactions) 


# for i in range(num_reactions):
    # reaction_Qs[i] = allQ[reaction_id[i]]
    # reaction_neuQs[i] = allQneu[reaction_id[i]]



# # net_get function parameters
# just_dxdt = False
# n = {}
# num_isos = species
# x=np.zeros(num_isos)
# x[:]=10**-99

# x[net_lib.ih1.get()] = 0.5
# x[net_lib.ihe4.get()] = 0.5

# temp = 10**9
# log10temp = np.log10(temp)
# rho = 10**9
# log10rho = np.log10(rho)

# abar = 0.75
# zbar = 0.75
# z2bar = 0.5
# ye = 1.0

# eta = 0.0
# d_eta_dlnT = 0.0
# d_eta_dlnRho = 0.0

# rate_factors = np.zeros(num_reactions)
# rate_factors[:]=1.0
# weak_rate_factor = 1.0

# reuse_rate_raw = False
# reuse_rate_screened = False

# #Outs

# eps_nuc = 0.0
# d_eps_nuc_dT = 0.0
# d_eps_nuc_dRho = 0.0
# d_eps_nuc_dx = np.zeros(num_isos)
# dxdt = np.zeros(num_isos)
# d_dxdt_dRho = np.zeros(num_isos)
# d_dxdt_dT = np.zeros(num_isos)
# d_dxdt_dx = np.zeros((num_isos,num_isos))

# eps_nuc_categories = np.zeros(chem_def.num_categories.get())
# eps_neu_total = 0.0
# screening_mode = 0
# theta_e_for_graboske_et_al = 0.0        
# lwork = net_lib.net_work_size(handle, ierr) 

# work = np.zeros(lwork)
# ierr = 0

# res = net_lib.net_get( 
            # handle, just_dxdt, n, num_isos, num_reactions,  
            # x, temp, log10temp, rho, log10rho,  
            # abar, zbar, z2bar, ye, eta, d_eta_dlnT, d_eta_dlnRho, 
            # rate_factors, weak_rate_factor, 
            # reaction_Qs, reaction_neuQs, reuse_rate_raw, reuse_rate_screened, 
            # eps_nuc, d_eps_nuc_dRho, d_eps_nuc_dT, d_eps_nuc_dx,  
            # dxdt, d_dxdt_dRho, d_dxdt_dT, d_dxdt_dx,  
            # screening_mode, theta_e_for_graboske_et_al,
            # eps_nuc_categories, eps_neu_total, 
            # lwork, work, ierr)



