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

    temp=kwargs['t']
    den=kwargs['r']
    
    reac_id=kwargs['reac_id']

    logT = crlibm_lib.log10_cr(temp)
    logRho = crlibm_lib.log10_cr(den)

    rate_raw=0.0
    rate_raw_dT=0.0
    rate_raw_dRho=0.0
    
    result = net_lib.net_get_rate_simple(
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
    # plt.show()
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

if pym.MESA_VERSION >= 10000:
     #Function sig changed
     rates_lib.rates_init('reactions.list','jina_reaclib_results_20130213default2',
                    'rate_tables',False,False,'','','',ierr)
else:
     rates_lib.rates_init('reactions.list','jina_reaclib_results_20130213default2',
                    'rate_tables',False,'','','',ierr)

if pym.MESA_VERSION >= 10398:
    kap_lib.kap_init('gs98','gs98_co','lowT_fa05_gs98',3.88,3.80,True,pym.KAP_CACHE,'',ierr)
else:
    kap_lib.kap_init('gs98','gs98_co','lowT_fa05_gs98',3.88,3.80,3.80,True,pym.KAP_CACHE,'',ierr)

ion_lib.ionization_init('ion','',pym.ION_CACHE,True,ierr)
net_lib.net_init(ierr)
eos_lib.eos_init('mesa','','','',True,ierr)
                
                

net_file = os.path.join(pym.NETS,'mesa_201.net')

                
# Net setup
net_lib.net_init(ierr)
handle=net_lib.alloc_net_handle(ierr)
net_lib.net_start_def(handle, ierr)
net_lib.read_net_file(net_file, handle, ierr)
net_lib.net_finish_def(handle, ierr)

net_lib.net_set_logtcut(handle, -1,-1, ierr)
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


ierr=0

extra_args={'reac_id':rates_def.ir_s32_ap_cl35.get()}

# print(eval_x(test_var='r',arg='t',arg2='r',log=True,t=10**8.0,r=10**8,
      # **extra_args,deriv=False))
      
num=100

xmin=10**7.0
xmax=10**10.0

plot2d(xmin,xmax,xmin,xmax,num,num,'rates_rev_t',title='dR/dt',**extra_args,
    test_var='t',arg='t',arg2='r',log=True,rev=True)

plot2d(xmin,xmax,xmin,xmax,num,num,'rates_rev_r',title='dR/drho',**extra_args,
    test_var='r',arg='r',arg2='t',log=True,rev=False)

plotRaw(xmin,xmax,xmin,xmax,num,num,'rates_rev',title='R',**extra_args,
    test_var='t',arg='t',arg2='r',log=True,rev=True,deriv=False,logvalue=True)


extra_args={'reac_id':rates_def.ir_cl35_pa_s32.get()}

plot2d(xmin,xmax,xmin,xmax,num,num,'rates_t',title='dR/dt',**extra_args,
    test_var='t',arg='t',arg2='r',log=True,rev=True)

plot2d(xmin,xmax,xmin,xmax,num,num,'rates_r',title='dR/drho',**extra_args,
    test_var='r',arg='r',arg2='t',log=True,rev=False)

plotRaw(xmin,xmax,xmin,xmax,num,num,'rates',title='R',**extra_args,
    test_var='t',arg='t',arg2='r',log=True,rev=True,deriv=False,logvalue=True)


