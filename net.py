from __future__ import print_function
import pyMesaUtils as pym
import numpy as np
import os

eos_lib, eos_def = pym.loadMod("eos")
const_lib, const_def = pym.loadMod("const")
crlibm_lib, _ = pym.loadMod("crlibm")
chem_lib, chem_def = pym.loadMod("chem")
net_lib, net_def = pym.loadMod("net")
rates_lib, rates_def = pym.loadMod("rates")
kap_lib, kap_def = pym.loadMod("kap")
ion_lib, ion_def = pym.loadMod("ionization")

ierr=0

crlibm_lib.crlibm_init()
const_lib.const_init(pym.MESA_DIR,ierr)
chem_lib.chem_init('isotopes.data',ierr)
rates_lib.rates_init('reactions.list','jina_reaclib_results_20130213default2',
                    'rate_tables',False,'','','',ierr)
kap_lib.kap_init('gs98','gs98_co','lowT_fa05_gs98',3.88,3.80,3.80,False,pym.KAP_CACHE,'',ierr)
ion_lib.ionization_init('ion','',pym.ION_CACHE,False,ierr)
net_lib.net_init(ierr)
eos_lib.eos_init('mesa','','','',False,ierr)
                
                

net_file = os.path.join(pym.NETS,'mesa_45.net')

                
# Net setup
net_lib.net_init(ierr)
handle=net_lib.alloc_net_handle(ierr)
net_lib.net_start_def(handle, ierr)
net_lib.read_net_file(net_file, handle, ierr)
net_lib.net_finish_def(handle, ierr)

#res = net_lib.net_ptr(handle, g, ierr)
# Has issues with the g pointer so set manually for now
species = 45
num_reactions = 367

which_rates = np.zeros(rates_def.rates_reaction_id_max.get())
reaction_id = np.zeros(num_reactions)
which_rates[:] = 1
#rates_lib.set_which_rates(ierr)
net_lib.net_set_which_rates(handle, which_rates, ierr)
net_lib.net_setup_tables(handle, '', ierr)

# End net setup


# net_get function parameters
just_dxdt = False
n = {}
num_isos = species
x=np.zeros(num_isos)
x[:]=10**-99

x[net_lib.ih1.get()] = 0.5
x[net_lib.ihe4.get()] = 0.5

temp = 10**9
log10temp = np.log10(temp)
rho = 10**9
log10rho = np.log10(rho)
abar = 0.75
zbar = 0.75
z2bar = 0.5
ye = 1.0

eta = 0.0
d_eta_dlnT = 0.0
d_eta_dlnRho = 0.0

rate_factors = np.zeros(num_reactions)
rate_factors[:]=1.0
weak_rate_factor = 1.0


allQ = rates_def.std_reaction_qs.get()
allQneu = rates_def.std_reaction_neuqs.get()

reaction_Qs  = allQ # Not correct need to map ids properly using g pointer but good enough for testing
reaction_neuQs = allQneu # Not correct need to map ids properly using g pointer but good enough for testing
reuse_rate_raw = False
reuse_rate_screened = False

#Outs

eps_nuc = 0.0
d_eps_nuc_dT = 0.0
d_eps_nuc_dRho = 0.0
d_eps_nuc_dx = np.zeros(num_isos)
dxdt = np.zeros(num_isos)
d_dxdt_dRho = np.zeros(num_isos)
d_dxdt_dT = np.zeros(num_isos)
d_dxdt_dx = np.zeros((num_isos,num_isos))

eps_nuc_categories = np.zeros(chem_def.num_categories.get())
eps_neu_total = 0.0
screening_mode = 0
theta_e_for_graboske_et_al = 0.0        
lwork = net_lib.net_work_size(handle, ierr) 

work = np.zeros(lwork)
ierr = 0

res = net_lib.net_get( 
            handle, just_dxdt, n, num_isos, num_reactions,  
            x, temp, log10temp, rho, log10rho,  
            abar, zbar, z2bar, ye, eta, d_eta_dlnT, d_eta_dlnRho, 
            rate_factors, weak_rate_factor, 
            reaction_Qs, reaction_neuQs, reuse_rate_raw, reuse_rate_screened, 
            eps_nuc, d_eps_nuc_dRho, d_eps_nuc_dT, d_eps_nuc_dx,  
            dxdt, d_dxdt_dRho, d_dxdt_dT, d_dxdt_dx,  
            screening_mode, theta_e_for_graboske_et_al,
            eps_nuc_categories, eps_neu_total, 
            lwork, work, ierr)



