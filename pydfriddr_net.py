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

    T=kwargs['t']
    rho=kwargs['rho']


    just_dxdt = False
    num_isos = species
    x=np.zeros(num_isos)
    x[:]=10**-99
    
    x[net_iso[chem_def.ih1.get()-1]-1] =kwargs['h1']
    x[net_iso[chem_def.ihe4.get()-1]-1] = kwargs['he4']
    x[net_iso[chem_def.isi28.get()-1]-1] = kwargs['si28']
    x[net_iso[chem_def.ic12.get()-1]-1] = kwargs['c12']
    x[net_iso[chem_def.io16.get()-1]-1] = kwargs['o16']
    x[net_iso[chem_def.ife56.get()-1]-1] = kwargs['fe56']
    
    log10temp = crlibm_lib.log10_cr(T)
    log10rho = crlibm_lib.log10_cr(rho)
        
    # print(log10temp,log10rho,abar,zbar,z2bar,ye)
    # print(x[net_iso[chem_def.ih1.get()-1]-1],
    # x[net_iso[chem_def.ihe4.get()-1]-1],
    # x[net_iso[chem_def.isi28.get()-1]-1],
    # x[net_iso[chem_def.ic12.get()-1]-1],
    # x[net_iso[chem_def.io16.get()-1]-1],
    # x[net_iso[chem_def.ife56.get()-1]-1],)
    # print(x)
    
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
    ierr = 0
    
    net_lib.net_get_s.saveArgs(True)
    
    # print(log10temp, log10rho)
    
    res = net_lib.net_get_s( 
            handle,num_isos,
            x, T, log10temp, rho, log10rho,  
            allQ, allQneu, 
            eps_nuc, d_eps_nuc_dRho, d_eps_nuc_dT, d_eps_nuc_dx,  
            dxdt, d_dxdt_dRho, d_dxdt_dT, d_dxdt_dx,  
            eps_nuc_categories, eps_neu_total, 
            ierr)
 
 
    res=np.nan
    if deriv:
        if test_var is 't':
            res=net_lib.net_get_s.args_out['d_eps_nuc_dt'].value
        elif test_var is 'r':
            res=net_lib.net_get_s.args_out['d_eps_nuc_drho'].value
    else:
        res=net_lib.net_get_s.args_out['eps_nuc'].value      

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
    a[1,1] = a[1,1]-func(deriv=False,**kwargs) / (2.0*step) 
    if verbose: print('\tdfdx',1,a[1,1],start_step)
    for i in range(2,ntab):
        step=step/con
        
        kwargs[arg]=start_x+step
        a[1,i]=func(deriv=False,**kwargs)
        
        kwargs[arg]=start_x-step
        a[1,i]= a[1,i]- func(deriv=False,**kwargs) / (2.0*step)
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
    tmp=[]
    err=[]
    for j in range(0,15):
        kwargs['start_step']=kwargs[kwargs['arg']]/(10.0**j)
        kwargs['start_x']=kwargs[kwargs['arg']]
        r=eval_func(eval_x,eval_dx,False,**kwargs)
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
        z.append([])
        for j in yvalues:
            kwargs[kwargs['arg']]=10**i
            kwargs[kwargs['arg2']]=10**j
            r=bestfit(**kwargs)
            z[-1].append(np.log10(np.abs(r[3])))
    
    z=np.array(z)
    np.save(name,z)
    fig=plt.figure()
    ax=fig.add_subplot(111)
    extent=(xvalues.min(),xvalues.max(),yvalues.min(),yvalues.max())
    if kwargs['rev']:
        z=z.T
        extent=(yvalues.min(),yvalues.max(),xvalues.min(),xvalues.max())
    
    cax=ax.imshow(z.T,extent=extent,aspect='auto',vmin=np.maximum(np.min(z),-16.0),vmax=0.0,origin='lower')
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

rates_lib.rates_init('reactions.list','jina_reaclib_results_20130213default2',
                    'rate_tables',False,False,'','','',ierr)

net_file = os.path.join(pym.NETS,'mesa_45.net')

                
# Net setup
net_lib.net_init(ierr)
handle=net_lib.alloc_net_handle(ierr)
net_lib.net_start_def(handle, ierr)
net_lib.read_net_file(net_file, handle, ierr)
net_lib.net_finish_def(handle, ierr)

net_lib.net_set_logTcut(handle, -1,-1, ierr)
net_lib.net_set_fe56ec_fake_factor(handle, 10**-7, 3.0*10**9, ierr)

g={}
res = net_lib.net_ptr(handle, g, ierr)
g=res['g'] # Note this is only a copy of the pointer, changes wont propagate back to mesa

species = g['num_isos']
num_reactions = g['num_reactions']

rates_reaction_id_max = rates_def.rates_reaction_id_max.get()

which_rates = np.zeros(rates_def.rates_reaction_id_max.get())
reaction_id = np.zeros(num_reactions)
which_rates[:] = rates_def.rates_jr_if_available.get()
#rates_lib.set_which_rates(ierr)
net_lib.net_set_which_rates(handle, which_rates, ierr)
net_lib.net_setup_tables(handle, '', ierr)

# End net setup


num_chem_isos = chem_def.num_chem_isos.get()

chem_id=np.zeros(num_chem_isos)
net_iso_table=np.zeros(num_chem_isos)
         
res=net_lib.get_chem_id_table(handle, species, chem_id, ierr)
chem_id = res['chem_id']

res=net_lib.get_net_iso_table(handle, net_iso_table, ierr)
net_iso = np.array(res['net_iso_table'])

res=net_lib.get_reaction_id_table(handle, num_reactions, reaction_id, ierr)
reaction_id = res['reaction_id']
 
reaction_table=np.zeros(rates_reaction_id_max)        
res=net_lib.get_net_reaction_table(handle, reaction_table, ierr)

reaction_table = np.array(res['net_reaction_table'])

allQ = rates_def.std_reaction_qs.get()
allQneu = rates_def.std_reaction_neuqs.get()


rate_factors = np.zeros(num_reactions)
rate_factors[:]=1.0

#print(eval_x(10**9.0,'t',10**9.0,deriv=True))



print(eval_x(test_var='t',arg='t',arg2='r',log=True,t=10**9.0,rho=10**9,
      h1=0.0,he4=0.1,c12=0.1,o16=0.1,si28=0.5,fe56=0.2,deriv=False))

# print(eval_x(test_var='t',arg='t',arg2='r',log=True,t=10**9.0,rho=10**9,
        # h1=0.0,he4=0.1,c12=0.1,o16=0.1,si28=0.5,fe56=0.2,deriv=True))

# sys.exit()




prefix=sys.argv[1]


steps=50

tmin=10**7.5
tmax=10**10.0
rmin=10**5
rmax=10**10

j='t'
print("Start t")
plot2d(tmin,tmax,rmin,rmax,steps,steps,prefix+'_'+j+'_all.pdf',title='dt',
test_var='t',arg='t',arg2='rho',log=True,rev=False,
h1=0.0,he4=0.1,c12=0.1,o16=0.1,si28=0.5,fe56=0.2)

print("End t")

j='r'
print("Start r")
plot2d(rmin,rmax,tmin,tmax,steps,steps,prefix+'_'+j+'_all.pdf',title='drho',
test_var='r',arg='rho',arg2='t',log=True,rev=True,
h1=0.0,he4=0.1,c12=0.1,o16=0.1,si28=0.5,fe56=0.2)

print("End r")



# net_get_s
      # subroutine net_get_s( &
            # handle,num_isos, &
            # x, temp, log10temp, rho, log10rho,  &
            # reaction_Qs, reaction_neuQs, &
            # eps_nuc, d_eps_nuc_dRho, d_eps_nuc_dT, d_eps_nuc_dx,  &
            # dxdt, d_dxdt_dRho, d_dxdt_dT, d_dxdt_dx,  &
            # eps_nuc_categories, eps_neu_total, &
            # ierr)
         # use chem_def, only: num_categories
         # use chem_lib, only: basic_composition_info
         # use net_eval, only: eval_net
         # use net_def, only: Net_General_Info, Net_Info, get_net_ptr
         # use rates_def, only: num_rvs, rates_reaction_id_max
      
         # ! provide T or logT or both (the code needs both, so pass 'em if you've got 'em!)
         # ! same for Rho and logRho
      
         # integer, intent(in) :: handle
         # integer, intent(in) :: num_isos
         # real(dp), intent(in)  :: x(num_isos) ! (num_isos)
         # real(dp), intent(in)  :: temp, log10temp ! log10 of temp
            # ! provide both if you have them.  else pass one and set the other to = arg_not_provided
            # ! "arg_not_provided" is defined in mesa const_def
         # real(dp), intent(in)  :: rho, log10rho ! log10 of rho
            # ! provide both if you have them.  else pass one and set the other to = arg_not_provided
            # ! "arg_not_provided" is defined in mesa const_def
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
         # real(dp) :: weak_rate_factor = 1d0
         # real(dp), pointer, intent(in) :: reaction_Qs(:) ! (rates_reaction_id_max)
         # real(dp), pointer, intent(in) :: reaction_neuQs(:) ! (rates_reaction_id_max)
         # real(dp), intent(out) :: eps_nuc ! ergs/g/s from burning after subtract reaction neutrinos
         # real(dp), intent(out) :: d_eps_nuc_dT
         # real(dp), intent(out) :: d_eps_nuc_dRho
         # real(dp), intent(inout) :: d_eps_nuc_dx(num_isos) ! (num_isos) 
            # ! partial derivatives wrt mass fractions
      
         # real(dp), intent(inout) :: dxdt(num_isos) ! (num_isos)
            # ! rate of change of mass fractions caused by nuclear reactions
         # real(dp), intent(inout) :: d_dxdt_dRho(num_isos) ! (num_isos)
         # real(dp), intent(inout) :: d_dxdt_dT(num_isos) ! (num_isos)
         # real(dp), intent(inout) :: d_dxdt_dx(num_isos,num_isos) ! (num_isos, num_isos)
            # ! partial derivatives of rates wrt mass fractions
            
         # real(dp), intent(inout) :: eps_nuc_categories(num_categories) ! (num_categories)
            # ! eps_nuc subtotals for each reaction category

         # real(dp), intent(out) :: eps_neu_total ! ergs/g/s neutrinos from weak reactions

         # integer :: lwork ! size of work >= result from calling net_work_size
         # real(dp), pointer :: work(:) ! (lwork)
         
         # integer, intent(out) :: ierr ! 0 means okay
                  
         # integer :: time0, time1
         # type (Net_General_Info), pointer :: g
         # real(dp), pointer, dimension(:) :: actual_Qs, actual_neuQs
         # logical, pointer :: from_weaklib(:) ! ignore if null
         # logical, parameter :: symbolic = .false.
         # logical, parameter :: rates_only = .false.
         # type (Net_Info), target :: net_info_target
         # type (Net_Info), pointer :: netinfo
          # real(dp) :: xh, xhe,xz, z, mass_correction, sumx
         # integer,dimension(num_isos) :: chem_id
         
         # actual_Qs => null()
         # actual_neuQs => null()
         # from_weaklib => null()

         # ierr = 0
         # call get_net_ptr(handle, g, ierr)
         # if (ierr /= 0) then
            # write(*,*) 'invalid handle for net_get -- did you call alloc_net_handle?'
            # return
         # end if
         
         # lwork=net_work_size(handle, ierr) 
         # allocate(work(lwork),rate_factors(g%num_reactions))
         # rate_factors= 1d0
         # netinfo => net_info_target
         
         # eta=0d0
         # d_eta_dlnT=0d0
         # d_eta_dlnRho=0d0
         
         # call get_chem_id_table(handle,g%num_isos,chem_id,ierr)
         
         # call basic_composition_info(g%num_isos, chem_id, x, xh, xhe, xz, &
            # abar, zbar, z2bar, ye, mass_correction,sumx)
         
         
         # call eval_net( &
               # netinfo, g, rates_only, .false., g%num_isos, g%num_reactions, g% num_wk_reactions, &
               # x, temp, log10temp, rho, log10rho,  &
               # abar, zbar, z2bar, ye, eta, d_eta_dlnT, d_eta_dlnRho, &
               # rate_factors, weak_rate_factor, &
               # reaction_Qs, reaction_neuQs, .false.,.false., &
               # eps_nuc, d_eps_nuc_dRho, d_eps_nuc_dT, d_eps_nuc_dx,  &
               # dxdt, d_dxdt_dRho, d_dxdt_dT, d_dxdt_dx,0, 0.d0,  &
               # eps_nuc_categories, eps_neu_total, &
               # lwork, work, actual_Qs, actual_neuQs, from_weaklib, symbolic, &
               # ierr)
         
         # deallocate(work)
         
      # end subroutine net_get_s
