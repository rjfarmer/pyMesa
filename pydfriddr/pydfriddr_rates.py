"""
This is an example on how to test the quality of MESA's derivatives using ridders method of polynomial extrapolation.

By defining a function in eval_x and eval_dx we can test how mesa derivatives handle changes in the x value. This
is already done in MESA in star/private/star_newton.f90 but its tightly coupled to the solver.
This way we can test the derivatives from the low level modules without needing to have a whole star setup.

It does mean though we can not test the compound derivatives inside hydro_eqns.

"""

import pyMesaUtils as pym
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import ctypes


def eval_x(**kwargs):
    """
    This should take the x value being tested and return y(x)
    
    """
    test_var=kwargs['test_var']
    deriv=kwargs['deriv']
    handle=kwargs['handle']

    temp=np.maximum(1.0,kwargs['t'])
    den=np.maximum(1.0,kwargs['r'])
    
    reac_id=kwargs['reac_id']

    logT = crlibm_lib.log10_cr(temp)
    logRho = crlibm_lib.log10_cr(den)

    rate_raw=0.0
    rate_raw_dT=0.0
    rate_raw_dRho=0.0
    
    result = net_lib.net_get_rates_simple(
            handle,logT,logRho,reac_id,
            rate_raw,rate_raw_dT,rate_raw_dRho)
    
    if deriv:
        if test_var is 't':
            res = result['rate_raw_dt']
        elif test_var is 'r':
            res = result['rate_raw_drho']
    else:
        res = result['rate_raw']      

    return res


def eval_dx(**kwargs):
    """
    This should take the x value being tested and return dy/dx at x
    
    """
    return eval_x(**kwargs,deriv=True)



def eval_func(func=eval_x,func_dx=eval_dx,verbose=True,**kwargs):
    """
    Evaluate a function and its derivative by using ridders method of polynomial extrapolation
    Coded taken from $MESA_DIR/star/private/star_newton.f90 dfridr function
    
    Inputs:
    start_x: Float, Point we wish to test
    start_step: Float, Starting step over which the function changes substantially
    func: Function, Function that takes as argument the start_x and returns y(start_x) being tested
    func_dx: Function, Function that takes as argument the start_x and returns the dy/dx at start_x
    
    Returns:
    MESA derivative: Float, MESA's estimate of the derivative at x
    ridder derivative: Float, ridder's estimate of the derivative at x 
    ridder error: Float, Absolute error estimate on ridders derivative (should be small compared to ridder derivative)
    Rel Error: Float, Relative difference between MESA and ridder's estimates
    
    """
    ntab=20+1 # Use fortran numbering and start at 1
    con2=2.0
    con=con2**0.5
    err=10**50
    safe=2.0
    dfridr=0.0
    a=np.zeros((ntab,ntab))
    step=kwargs['start_step']
    start_x=kwargs['start_x']
    
    arg=kwargs['arg']
    kwargs[arg]=start_x+step
    a[1,1] = func(deriv=False,**kwargs) 
    
    kwargs[arg]=start_x-step
    a[1,1] = (a[1,1]-func(deriv=False,**kwargs)) / (2.0*step) 
    if verbose: print('\tdfdx',1,a[1,1],step)
    for i in range(2,ntab):
        step=step/con
        
        kwargs[arg]=start_x+step
        a[1,i]=func(deriv=False,**kwargs)
        
        kwargs[arg]=start_x-step
        a[1,i]= (a[1,i]- func(deriv=False,**kwargs)) / (2.0*step)
        if verbose: print('\tdfdx',i,a[1,i],step)
        fac=con2
        for j in range(2,i+1):
            a[j,i]=(a[j-1,i]*fac - a[j-1,i-1])/(fac-1.0)
            fac=con2*fac
            errt=np.maximum(np.abs(a[j,i]-a[j-1,i]),np.abs(a[j,i]-a[j-1,i-1]))
            if errt < err:
                err=errt
                dfridr = a[j,i]
                if verbose: print('\t\tdfridr err',i,j,dfridr,err)
        if np.abs(a[i,i] - a[i-1,i-1]) >= safe*err:
            if verbose: print("Higher order is worse")
            break
        
    kwargs[arg]=start_x
    dvardx_0 = func_dx(**kwargs)
    xdum=(dfridr-dvardx_0)/(np.maximum(np.abs(dvardx_0),10**-50))
    if verbose: print()
    if verbose: print('analytic numeric err rel_diff',dvardx_0,dfridr,err,xdum)
    
    return dvardx_0,dfridr,err,xdum


def bestfit(**kwargs):
    kwargs.pop('deriv',None)
    tmp=[]
    err=[]
    for j in range(0,15):
        kwargs['start_step']=kwargs[kwargs['arg']]/(10.0**j)
        kwargs['start_x']=kwargs[kwargs['arg']]
        r=eval_func(eval_x,eval_dx,verbose=False,**kwargs)
        tmp.append(r)
        try:
            err.append(np.abs(r[2]/r[1]))
        except ZeroDivisionError:
            err.append(np.nan)
        
    try:
        best_fit=np.nanargmin(err)
    except:
        best_fit=-1
        
    if best_fit>=0 and err[best_fit] < kwargs['tol']:
        r=tmp[best_fit]
    else:
        print("Failed for "+str(kwargs[kwargs['arg']]))
    
    return r

def plot2d(xmin,xmax,ymin,ymax,xsteps,ysteps,name,title='',**kwargs):    
    
    if kwargs['log']:
        xvalues=np.linspace(np.log10(xmin),np.log10(xmax),int(xsteps))
        yvalues=np.linspace(np.log10(ymin),np.log10(ymax),int(ysteps))
    else:
        xvalues=np.log10(np.linspace(xmin,xmax,int(xsteps)))
        yvalues=np.log10(np.linspace(ymin,ymax,int(ysteps)))
    
    kwargs['tol']=10**-3
    z=[]
    
    for i in xvalues:
        print(i)
        z.append([])
        for j in yvalues:
            kwargs[kwargs['arg']]=10**i
            kwargs[kwargs['arg2']]=10**j
            r=bestfit(**kwargs)
            z[-1].append(np.log10(np.abs(r[3])))
    
    z=np.array(z)
    fig=plt.figure()
    ax=fig.add_subplot(111)
    extent=(xvalues.min(),xvalues.max(),yvalues.min(),yvalues.max())
    if kwargs['rev']:
        z=z.T
        extent=(yvalues.min(),yvalues.max(),xvalues.min(),xvalues.max())
    
    cax=ax.imshow(z.T,extent=extent,aspect='auto',vmin=-16.0,vmax=0.0,origin='lower')
    cb=fig.colorbar(cax)
    
    cb.set_label('log abs dfriddr err')
    ax.set_title(title)
    
    if  kwargs['rev']:
        ax.set_xlabel(kwargs['arg2'])
        ax.set_ylabel(kwargs['arg'])
    else:
        ax.set_xlabel(kwargs['arg'])
        ax.set_ylabel(kwargs['arg2'])
    
    fig.savefig(name)
    #plt.show()
    plt.close(fig)
    
def plotRaw(xmin,xmax,ymin,ymax,xsteps,ysteps,name,title='',**kwargs):    
    
    if kwargs['log']:
        xvalues=np.linspace(np.log10(xmin),np.log10(xmax),int(xsteps))
        yvalues=np.linspace(np.log10(ymin),np.log10(ymax),int(ysteps))
    else:
        xvalues=np.log10(np.linspace(xmin,xmax,int(xsteps)))
        yvalues=np.log10(np.linspace(ymin,ymax,int(ysteps)))
    
    kwargs['tol']=10**-3
    z=[]
    
    for i in xvalues:
        print(i)
        z.append([])
        for j in yvalues:
            kwargs[kwargs['arg']]=10**i
            kwargs[kwargs['arg2']]=10**j
            r=eval_x(**kwargs)
            z[-1].append(r)
            

    z=np.array(z)
    if kwargs['logvalue']:
        z=np.log10(np.abs(z))
    
    fig=plt.figure()
    ax=fig.add_subplot(111)
    extent=(xvalues.min(),xvalues.max(),yvalues.min(),yvalues.max())
    if kwargs['rev']:
        z=z.T
        extent=(yvalues.min(),yvalues.max(),xvalues.min(),xvalues.max())
    
    cax=ax.imshow(z.T,extent=extent,aspect='auto',origin='lower')
    cb=fig.colorbar(cax)
    
    if kwargs['logvalue']:
        cb.set_label('log abs value')
    else:
        cb.set_label('value')
    ax.set_title(title)
    
    if  kwargs['rev']:
        ax.set_xlabel(kwargs['arg2'])
        ax.set_ylabel(kwargs['arg'])
    else:
        ax.set_xlabel(kwargs['arg'])
        ax.set_ylabel(kwargs['arg2'])
    
    fig.savefig(name)
    # plt.show()
    plt.close(fig)
    

mod="net"
pym.buildModule(mod)


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

if pym.MESA_VERSION >= 11213:
    rates_lib.rates_init('reactions.list','jina_reaclib_results_20171020_default',
                    'rate_tables',False,False,'','','',ierr)
elif pym.MESA_VERSION >= 10000:
     #Function sig changed
     rates_lib.rates_init('reactions.list','jina_reaclib_results_20130213default2',
                    'rate_tables',False,False,'','','',ierr)
else:
     rates_lib.rates_init('reactions.list','jina_reaclib_results_20130213default2',
                    'rate_tables',False,'','','',ierr)

if pym.MESA_VERSION >= 11354:
    kap_lib.kap_init('gs98','gs98_co','lowT_fa05_gs98',3.88,3.80,True,pym.KAP_CACHE,'',False,ierr)        
elif pym.MESA_VERSION >= 10398:
    kap_lib.kap_init('gs98','gs98_co','lowT_fa05_gs98',3.88,3.80,True,pym.KAP_CACHE,'',ierr)
else:
    kap_lib.kap_init('gs98','gs98_co','lowT_fa05_gs98',3.88,3.80,3.80,True,pym.KAP_CACHE,'',ierr)

ion_lib.ionization_init('ion','',pym.ION_CACHE,True,ierr)
net_lib.net_init(ierr)
eos_lib.eos_init('mesa','','','',True,ierr)
                
                

net_file = os.path.join(pym.NETS,'cno_extras_o18_to_mg26_plus_fe56.net')

                
# Net setup
net_lib.net_init(ierr)
handle=net_lib.alloc_net_handle(ierr)
net_lib.net_start_def(handle, ierr)
net_lib.read_net_file(net_file, handle, ierr)
net_lib.net_finish_def(handle, ierr)

net_lib.net_set_logtcut(handle, -1,-1, ierr)
net_lib.net_set_fe56ec_fake_factor(handle, 10**-7, 3.0*10**9, ierr)

species = net_lib.net_num_isos(handle, ierr)
num_reactions =  net_lib.net_num_reactions(handle, ierr)

rates_reaction_id_max = rates_def.rates_reaction_id_max.get()

which_rates = np.zeros(rates_def.rates_reaction_id_max.get())
reaction_id = np.zeros(num_reactions)
which_rates[:] = rates_def.rates_jr_if_available.get()
#rates_lib.set_which_rates(ierr)
net_lib.net_set_which_rates(handle, which_rates, ierr)
net_lib.net_setup_tables(handle, '', ierr)


rates_lib.rates_warning_init(False,10.0)
# End net setup


#net_lib.show_net_reactions(handle,0,ierr)

ierr=0

rate_names=['r34_pp2',
'r34_pp3',
'r_c12_ag_o16',
'r_c12_ap_n15',
'r_c12_pg_n13',
'r_c13_pg_n14',
'r_f17_ap_ne20',
'r_f17_gp_o16',
'r_f17_pa_o14',
'r_f17_pg_ne18',
'r_f17_wk_o17',
'r_f18_gp_o17',
'r_f18_pa_o15',
'r_f18_pg_ne19',
'r_f18_wk_o18',
'r_f19_gp_o18',
'r_f19_pa_o16',
'r_f19_pg_ne20',
'r_h1_he3_wk_he4',
'r_he3_he3_to_h1_h1_he4',
'r_he4_he4_he4_to_c12',
'r_mg22_ga_ne18',
'r_n13_ap_o16',
'r_n13_gp_c12',
'r_n13_pg_o14',
'r_n13_wk_c13',
'r_n14_ag_f18',
'r_n14_ap_o17',
'r_n14_gp_c13',
'r_n14_pg_o15',
'r_n15_ag_f19',
'r_n15_ap_o18',
'r_n15_pa_c12',
'r_n15_pg_o16',
'r_ne18_ag_mg22',
'r_ne18_gp_f17',
'r_ne18_wk_f18',
'r_ne19_ga_o15',
'r_ne19_gp_f18',
'r_ne19_wk_f19',
'r_ne20_ag_mg24',
'r_ne20_gp_f19',
'r_ne22_ag_mg26',
'r_o14_ag_ne18',
'r_o14_ap_f17',
'r_o14_gp_n13',
'r_o14_wk_n14',
'r_o15_ag_ne19',
'r_o15_ap_f18',
'r_o15_gp_n14',
'r_o15_wk_n15',
'r_o16_ag_ne20',
'r_o16_ap_f19',
'r_o16_gp_n15',
'r_o16_pg_f17',
'r_o17_pa_n14',
'r_o17_pg_f18',
'r_o18_ag_ne22',
'r_o18_pa_n15',
'r_o18_pg_f19',
'rbe7ec_li7_aux',
'rbe7pg_b8_aux',
'rc12ap_aux',
'rn14ag_to_o18',
'rn14pg_aux',
'rna23pa_aux',
'rna23pg_aux',
'rne18ap_to_mg22',
'rne19pg_to_mg22',
'rne20ap_aux',
'rne20ap_to_mg24',
'rne20pg_to_mg22',
'ro16gp_aux',
'rpep_to_he3',
'rpp_to_he3']

for rate in rate_names[24:]:
#for rate in ['r_c12_ag_o16']:
    print(rate)
    y=rates_lib.rates_reaction_id(rate)
    if y==0:
        raise ValueError("Bad reaction id")

    extra_args={'reac_id':y,'handle':handle,'reac_name':rate}

    num=20

    xmin=10**8.0
    xmax=10**10.0

    plot2d(xmin,xmax,xmin,xmax,num,num,rate+'_dt.pdf',title=rate +' dR/dt',**extra_args,
        test_var='t',arg='t',arg2='r',log=True,rev=True)

    plot2d(xmin,xmax,xmin,xmax,num,num,rate+'_drho.pdf',title=rate + ' dR/drho',**extra_args,
         test_var='r',arg='r',arg2='t',log=True,rev=False)

    plotRaw(xmin,xmax,xmin,xmax,num,num,rate+'_rate.pdf',title=rate+' raw',**extra_args,
        test_var='t',arg='t',arg2='r',log=True,rev=True,deriv=False,logvalue=True)
        


# subroutine net_get_rates_simple(handle,logT,logRho,reac_id, &
            # rate_raw,rate_raw_dT,rate_raw_dRho)
    
        # use rates_def
        # use net_def
        # use net_eval
         # integer, intent(in) :: handle, reac_id
         # integer :: ierr
         # real(dp), intent(in) :: logT,logRho
         # real(dp), intent(out) :: rate_raw,rate_raw_dT,rate_raw_dRho

         # real(dp), pointer, dimension(:) :: actual_Qs, actual_neuQs
         # logical, pointer :: from_weaklib(:) ! ignore if null
         # logical, parameter :: symbolic = .false.
         # logical, parameter :: rates_only = .false.
         # type (Net_General_Info), pointer :: g

         # type(Net_Info),target :: n1
            # type(Net_Info),pointer :: n

         # real(dp)  :: abar  ! mean number of nucleons per nucleus
         # real(dp)  :: zbar  ! mean charge per nucleus
         # real(dp)  :: z2bar ! mean charge squared per nucleus
         # real(dp)  :: ye    
            # ! mean number free electrons per nucleon, assuming complete ionization
            # ! d_dxdt_dx(i, j) is d_dxdt(i)_dx(j), 
            # ! i.e., partial derivative of rate for i'th isotope wrt j'th isotope abundance
         # real(dp)  :: eta, d_eta_dlnT, d_eta_dlnRho ! electron degeneracy from eos.
            # ! this arg is only used for prot(e-nu)neut and neut(e+nu)prot.
            # ! if your net doesn't include those, you can safely ignore this arg.
         # real(dp), pointer :: rate_factors(:) ! (num_reactions)
            # ! when rates are calculated, they are multiplied by the
            # ! corresponding values in this array.
            # ! rate_factors array is indexed by reaction number.
            # ! use net_reaction_table to map reaction id to reaction number.
         # real(dp) :: weak_rate_factor = 1.0
         # real(dp), pointer :: reaction_Qs(:) ! (rates_reaction_id_max)
         # real(dp), pointer :: reaction_neuQs(:) ! (rates_reaction_id_max)
    

         # logical :: reuse_rate_raw=.false., reuse_rate_screened=.false. ! if true. use given rate_screened

         # real(dp) :: eps_nuc ! ergs/g/s from burning after subtract reaction neutrinos
         # real(dp) :: d_eps_nuc_dT
         # real(dp) :: d_eps_nuc_dRho
         # real(dp),allocatable :: d_eps_nuc_dx(:),x(:) ! (num_isos) 
            # ! partial derivatives wrt mass fractions
      
         # real(dp),allocatable:: dxdt(:) ! (num_isos)
            # ! rate of change of mass fractions caused by nuclear reactions
         # real(dp),allocatable :: d_dxdt_dRho(:) ! (num_isos)
         # real(dp),allocatable :: d_dxdt_dT(:) ! (num_isos)
         # real(dp),allocatable :: d_dxdt_dx(:,:) ! (num_isos, num_isos)
            # ! partial derivatives of rates wrt mass fractions
            
         # real(dp) :: eps_nuc_categories(num_categories) ! (num_categories)
            # ! eps_nuc subtotals for each reaction category

         # real(dp) :: eps_neu_total ! ergs/g/s neutrinos from weak reactions

         # integer :: screening_mode = 0, num_isos
         # ! if true, use the screening scheme defined in the following papers:
            # ! DeWitt, Graboske, Cooper, "Screening Factors for Nuclear Reactions. 
            # !    I. General Theory", ApJ, 181:439-456, 1973.
            # ! Graboske, DeWitt, Grossman, Cooper, "Screening Factors for Nuclear Reactions. 
            # !    II. Intermediate Screening and Astrophysical Applications", ApJ, 181:457-474, 1973.
         # ! if false, use the screening scheme from Frank Timmes which is based on the following:
            # !..graboske, dewit, grossman and cooper apj 181 457 1973, for weak screening. 
            # !..alastuey and jancovici apj 226 1034 1978, for strong screening. 
            # !..itoh et al apj 234 1079 1979, plasma parameters for strong screening. 
            # !..see also, 
            # !..wallace & woosley 1982, apj, 258, 696, appendix a.
            # !..calder et al, 2007, apj, 656, 313.    
         # real(dp)  :: theta_e_for_graboske_et_al = 0.d0
            # ! if screening_mode is true,
            # ! then theta_e is used to quantify the freezing-out of degenerate electrons
            # ! (see paper I by DeWitt, Graboske, Cooper, equation number 5).
            # ! theta_e goes to 1 for non-degenerate electrons and to 0 for large degeneracy.
            # ! the mesa/eos routine eos_theta_e computes this as a function of T and eta.
            
         # integer :: lwork ! size of work >= result from calling net_work_size
         # real(dp), pointer :: work(:) ! 
         # integer :: info

         # actual_Qs => null()
         # actual_neuQs => null()
         # from_weaklib => null()

        # n => n1
         
         # lwork = net_work_size(handle,ierr)
         # call get_net_ptr(handle, g, ierr)
         
         # num_isos = g%num_isos
         
         # allocate(dxdt(num_isos),d_dxdt_dRho(num_isos),x(num_isos),&
                  # d_eps_nuc_dx(num_isos),d_dxdt_dT(num_isos),d_dxdt_dx(num_isos, num_isos))

        # allocate(rate_factors(g%num_reactions),work(lwork))

        # x = 1d-99
        # x(1) = 1.d0

        # rate_factors = 1.d0

        # reaction_Qs => std_reaction_qs
       # reaction_neuQs => std_reaction_neuqs

    
        # abar = 10.d0
        # zbar = 10.d0
        # z2bar = 10.d0
        # ye = 0.5d0
        # eta = 0.d0
        # d_eta_dlnT = 0.d0
        # d_eta_dlnRho = 0.d0

         
         # call eval_net( &
               # n, g, .true., .false., g%num_isos, g%num_reactions, g% num_wk_reactions, &
               # x, exp10_cr(logT), logT, exp10_cr(logRho), logRho,  &
               # abar, zbar, z2bar, ye, eta, d_eta_dlnT, d_eta_dlnRho, &
               # rate_factors, weak_rate_factor, &
               # reaction_Qs, reaction_neuQs, reuse_rate_raw, reuse_rate_screened, &
               # eps_nuc, d_eps_nuc_dRho, d_eps_nuc_dT, d_eps_nuc_dx,  &
               # dxdt, d_dxdt_dRho, d_dxdt_dT, d_dxdt_dx,  &
               # screening_mode, theta_e_for_graboske_et_al,  &
               # eps_nuc_categories, eps_neu_total, &
               # lwork, work, actual_Qs, actual_neuQs, from_weaklib, symbolic, &
               # ierr)

            # info =  g% reaction_id(reac_id)
            # rate_raw = n% rate_raw(info)
            # rate_raw_dT =n% rate_raw_dt(info)
            # rate_raw_dRho = n% rate_raw_drho(info)

    # end subroutine net_get_rates_simple
