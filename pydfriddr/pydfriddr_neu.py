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


def eval_x(x,*args,**kwargs):
    """
    This should take the x value being tested and return y(x)
    
    """
    test_var=args[0]
    deriv=kwargs['deriv']

    if test_var is 't':
        index=neu_def.idneu_dT.get()-1
        T=x
        rho,abar,zbar=args[1:4]
    elif test_var is 'r':
        index=neu_def.idneu_dRho.get()-1
        rho=x
        T,abar,zbar=args[1:4]
    elif test_var is 'a':
        index=neu_def.idneu_dabar.get()-1
        abar=x
        T,rho,zbar=args[1:4]
    elif test_var is 'z':
        index=neu_def.idneu_dzbar.get()-1
        zbar=x
        T,rho,abar=args[1:4]

    log10_T=crlibm_lib.log10_cr(T)
    log10_Rho=crlibm_lib.log10_cr(rho)
    z2bar=zbar*zbar
    
    log10_Tlim=7.5
    flags=np.zeros(neu_def.num_neu_types.get())
    #flags[:]=True
    flags[:]=False
    if args[4] >= 0:
        flags[args[4]]=True
    else:
        # flags[3]=True
        flags[:]=True
        # flags[-1]=False
    info=0
    
    num_neu_rvs=neu_def.num_neu_rvs.get()
    num_neu_types=neu_def.num_neu_types.get()
    loss=np.zeros(num_neu_rvs)
    sources=np.zeros((num_neu_types,num_neu_rvs))
    
    mass= 10**4
    
    res = neu_lib.neu_get(T, log10_T, rho, log10_Rho, abar, zbar, z2bar, log10_Tlim, flags, loss, sources,mass, info)
    if not deriv:
        index=neu_def.ineu.get()-1
        
    return res['loss'][index]


def eval_dx(x,*args,**kwargs):
    """
    This should take the x value being tested and return dy/dx at x
    
    """
    return eval_x(x,*args,deriv=True)



def eval_func(start_x,start_step,func=eval_x,func_dx=eval_dx,verbose=True,*args):
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
    step=start_step
    a[1,1] = (func(start_x+step,*args,deriv=False) - func(start_x-step,*args,deriv=False)) / (2.0*step) 
    if verbose: print('\tdfdx',1,a[1,1],start_step)
    for i in range(2,ntab):
        step=step/con
        a[1,i]=(func(start_x+step,*args,deriv=False) - func(start_x-step,*args,deriv=False)) / (2.0*step)
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
        
    dvardx_0 = func_dx(start_x,*args)
    xdum=(dfridr-dvardx_0)/(np.maximum(np.abs(dvardx_0),10**-50))
    if verbose: print()
    if verbose: print('analytic numeric err rel_diff',dvardx_0,dfridr,err,xdum)
    
    return dvardx_0,dfridr,err,xdum


def bestfit(x,*args):
    tmp=[]
    err=[]
    tol=10**-3
    for j in range(1,10):
        start_step=x/(10.0**j)
        r=eval_func(x,start_step,eval_x,eval_dx,False,*args)
        tmp.append(r)
        try:
            err.append(np.abs(r[2]/r[1]))
        except ZeroDivisionError:
            err.append(np.nan)
       
    try:
        best_fit=np.nanargmin(err)
    except:
        best_fit=-1
        
    if best_fit>=0 and err[best_fit] < tol:
        r=tmp[best_fit]
    else:
        print("Failed for "+str(x))
    
    return r

def driver(xmin,xmax,num_steps,log=False,tol=10**-6,*args):

    if log:
        xvalues=np.linspace(np.log10(xmin),np.log10(xmax),num_steps)
        xvalues=10**xvalues
    else:
        xvalues=np.linspace(xmin,xmax,num_steps)

    res=[]
    for i in xvalues:
        res.append(bestfit(i,args))
    
    return res
    
def plot1d(xmin,xmax,xsteps):    
    xvalues=np.linspace(np.log10(xmin),np.log10(xmax),xsteps)
        
    z=[]
    for i in xvalues:
       # print(i,j)
        r=bestfit(10**i,0,10**9.0,56.0,26.0)
        z[-1].append(np.log10(np.abs(r[3])))
    
    plt.ylabel('log abs dfriddr err')
    plt.plot(x,z)
    plt.scatter(x,z)
    plt.show()
    
    
def plot2d(xmin,xmax,ymin,ymax,xsteps,ysteps,deriv_flag,neu_flag,name,rev=False,title=''):    
    
    xvalues=np.linspace(np.log10(xmin),np.log10(xmax),int(xsteps))
    yvalues=np.linspace(np.log10(ymin),np.log10(ymax),int(ysteps))
    
        
    z=[]
    
    for i in xvalues:
        z.append([])
        for j in yvalues:
            #print(i,j)
            r=bestfit(10**i,deriv_flag,10**j,56.0,26.0,neu_flag)
            z[-1].append(np.log10(np.abs(r[3])))
    
    z=np.array(z)
    fig=plt.figure()
    ax=fig.add_subplot(111)
    
    extent=(np.log10(xmin),np.log10(xmax),np.log10(ymin),np.log10(ymax))
    if rev:
        z=z.T
        extent=(np.log10(ymin),np.log10(ymax),np.log10(xmin),np.log10(xmax))
    
    cax=ax.imshow(z.T,extent=extent,aspect='auto',vmin=np.maximum(np.min(z),-16.0),vmax=0.0,origin='lower')
    cb=fig.colorbar(cax)
    
    cb.set_label('log abs dfriddr err')
    ax.set_title(title)
    ax.set_xlabel('logT')
    ax.set_ylabel('LogRho')
    fig.savefig(name)
    plt.close(fig)
    
def plot2dNeu(xmin,xmax,ymin,ymax,xsteps,ysteps,name):    
    deriv_flag='t'
    neu_flag=-1
    title='nu'
    rev=False
    
    xvalues=np.linspace(np.log10(xmin),np.log10(xmax),int(xsteps))
    yvalues=np.linspace(np.log10(ymin),np.log10(ymax),int(ysteps))
    
        
    z=[]
    
    for i in xvalues:
        z.append([])
        for j in yvalues:
            z[-1].append(np.log10(eval_x(10**i,'t',10**j,56,26,3,deriv=False)))
    
    z=np.array(z)
    fig=plt.figure()
    ax=fig.add_subplot(111)
    
    extent=(np.log10(xmin),np.log10(xmax),np.log10(ymin),np.log10(ymax))

    cax=ax.imshow(z.T,extent=extent,aspect='auto',origin='lower',cmap='bwr')
    cb=fig.colorbar(cax)
    
    cb.set_label('log abs neu ')
    ax.set_title(title)
    ax.set_xlabel('logT')
    ax.set_ylabel('LogRho')
    fig.savefig(name)
    plt.close(fig)
    


mod="neu"


pym.buildModule(mod)

const_lib, const_def = pym.loadMod("const")
crlibm_lib, _ = pym.loadMod("crlibm")
ierr=0

crlibm_lib.crlibm_init()
const_lib.const_init(pym.MESA_DIR,ierr)

neu_lib,neu_def = pym.loadMod(mod)
#print(eval_x(10**9.0,'r',10**10.1,56,26,3,deriv=False))

#print(eval_func(10**9.0,10**0.0,eval_x,eval_dx,False,'t',10**2.0,56,26,4))

prefix=sys.argv[1]


steps=100

tmin=10**6.9
tmax=10**10.0
rmin=10**-1
rmax=10**10

j='t'
plot2d(tmin,tmax,rmin,rmax,steps,steps,j,-1,prefix+'_'+j+'_all.pdf',title='dt')
# for i in range(0,5):
    # print(j,i)
    # plot2d(tmin,tmax,rmin,rmax,steps,steps,j,i,prefix+'_'+j+'_'+str(i)+'.pdf',title='dt')


j='r'
plot2d(rmin,rmax,tmin,tmax,steps,steps,j,-1,prefix+'_'+j+'_all.pdf',rev=True,title='drho')
# for i in range(0,5):
    # print(j,i)
    # plot2d(rmin,rmax,tmin,tmax,steps,steps,j,i,prefix+'_'+j+'_'+str(i)+'.pdf',rev=True,title='drho')

plot2dNeu(tmin,tmax,rmin,rmax,steps,steps,prefix+'_neu.pdf')


