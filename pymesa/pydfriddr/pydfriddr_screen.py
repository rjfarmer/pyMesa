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

    logT = crlibm_lib.log10_cr(temp)
    logRho = crlibm_lib.log10_cr(den)

    abar = kwargs['a']
    zbar = kwargs['z']
    z2bar = 0.0
    
    a1 = kwargs['a1']
    z1 = kwargs['z1']
    a2 = kwargs['a2']
    z2 = kwargs['z2']
    
    ierr = 0
    
    scor = 0
    scordt = 0
    scordd = 0
    scorda = 0
    scordz = 0
    
    screen_res = rates_lib.screen_pair_simple( a1, z1, a2, z2, 
               abar, zbar, z2bar, 
               logT, logRho,
               scor,scordt,scordd,scorda,scordz)
    
    if deriv:
        if test_var is 't':
            res = screen_res['scordt']
        elif test_var is 'r':
            res = screen_res['scordd']
        elif test_var is 'a':
            res = screen_res['scorda']
        elif test_var is 'z':
            res = screen_res['scordz']
    else:
        res = screen_res['scor']      

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
        ax.set_xlabel('log '+kwargs['arg2'])
        ax.set_ylabel('log '+kwargs['arg'])
    else:
        ax.set_xlabel('log '+kwargs['arg'])
        ax.set_ylabel('log '+kwargs['arg2'])
    
    fig.savefig(name+'.pdf')
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
    

mod="rates"


pym.buildModule(mod)

const_lib, const_def = pym.loadMod("const")
crlibm_lib, _ = pym.loadMod("crlibm")
chem_lib, chem_def = pym.loadMod("chem")
rates_lib, rates_def = pym.loadMod("rates")


ierr=0

crlibm_lib.crlibm_init()
const_lib.const_init(pym.MESA_DIR,ierr)


#extra_args={'a1':28.0,'a2':28.0,'z1':14.0,'z2':14.0,'abar':14.0,'zbar':14.0,'z2bar':50.0}
#extra_args={'a1':1.0,'a2':1.0,'z1':1.0,'z2':1.0,'abar':1.0,'zbar':1.0,'z2bar':1.0}

# extra_args={'a1':12.0,'a2':12.0,'z1':6.0,'z2':6.0,'abar':12.0,'zbar':6.0,'z2bar':36.0}

#extra_args={'a1':100.0,'a2':100.0,'z1':50.0,'z2':50.0,'abar':100.0,'zbar':50.0,'z2bar':36.0}

#extra_args={'a1':208.0,'a2':4.0,'z1':100.0,'z2':2.0,'abar':100.0,'zbar':100.0,'z2bar':36.0}

# print(eval_x(test_var='r',arg='t',arg2='r',log=True,t=10**8.0,r=10**8,
      # **extra_args,deriv=False))
      
# num=100

# xmin=10**7.0
# xmax=10**10.0

# plot2d(xmin,xmax,xmin,xmax,num,num,'chug_t',title='dh0fit/dt',**extra_args,
    # test_var='t',arg='t',arg2='r',log=True,rev=True)

# plot2d(xmin,xmax,xmin,xmax,num,num,'chug_r',title='dh0fit/drho',**extra_args,
    # test_var='r',arg='r',arg2='t',log=True,rev=False)

# plotRaw(xmin,xmax,xmin,xmax,num,num,'chug_raw',title='h0fit',**extra_args,
    # test_var='t',arg='t',arg2='r',log=True,rev=True,deriv=False,logvalue=True)



#extra_args={'a1':12.0,'a2':12.0,'z1':6.0,'z2':6.0,'t':10**8.8,'r':10**6.0,'z2bar':36.0}
extra_args={'a1':56.0,'a2':4.0,'z1':26.0,'z2':2.0,'t':10**9.0,'r':10**9.0,'z2bar':36.0}

num=100

xmin= 1.0
xmax= 100.0
ymin = 1.0
ymax = 100.0


# plot2d(xmin,xmax,ymin,ymax,num,num,'chug_a_fe56he4',title='dh0fit/dabar',**extra_args,
    # test_var='a',arg='a',arg2='z',log=True,rev=True)

# plot2d(xmin,xmax,ymin,ymax,num,num,'chug_z_fe56he4',title='dh0fit/dzbar',**extra_args,
    # test_var='z',arg='z',arg2='a',log=True,rev=False)


print(rates_lib.screen_pair_simple( 56.0, 26.0, 4.0, 2.0, 56.0, 26.0, 0.0, 9.0, 9.0, 0.0,0.0,0.0,0.0,0.0))

sys.exit(0)

#############################

import pyMesaUtils as pym
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import ctypes


mod="rates"


pym.buildModule(mod)

const_lib, const_def = pym.loadMod("const")
crlibm_lib, _ = pym.loadMod("crlibm")
chem_lib, chem_def = pym.loadMod("chem")
rates_lib, rates_def = pym.loadMod("rates")


ierr=0

crlibm_lib.crlibm_init()
const_lib.const_init(pym.MESA_DIR,ierr)

rates_lib.screen_pair_simple( 12.0, 6.0, 12.0, 6.0, 12.0, 6.0, 0.0, 8.8, 6.0, 0.0,0.0,0.0,0.0,0.0)
rates_lib.screen_pair_simple( 28.0, 14.0, 28.0, 14.0, 28.0, 14.0, 0.0, 9.0, 9.0, 0.0,0.0,0.0,0.0,0.0)



