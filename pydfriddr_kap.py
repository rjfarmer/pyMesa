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
    arguments go as (value_to_be_tested,flag,other dependent variable, deriv=True/False)
    i.e for temp and rho  combination testing the temp its:
    (temp,'t',rho,deriv=True/False)
    """
    test_var=args[0]
    deriv=kwargs['deriv']

    if test_var is 't':
        logT=x/np.log(10.0)
        logRho=args[1]*np.log(10.0)
    elif test_var is 'r':
        logRho=x/np.log(10.0)
        logT=args[1]*np.log(10.0)

    handle = 1
    zbar = 1.0808603874105274
    X = 0.78
    Z = 0.02
    Zbase = 0.02
    XC=0.0
    XN=0.0
    XO=0.0
    XNe=0.0
    # XC = 0.0023225298690165287
    # XN = 0.000745982044130567
    # XO = 0.0061729948909251585
    # XNe = 0.0011784393788064082
    lnfree_e = -1.7540883425221482E-01
    d_lnfree_e_dlnRho= 1.5040256009583098E-02
    d_lnfree_e_dlnT= -6.8478280502896702E-03
    # lnfree_e = 0.0
    # d_lnfree_e_dlnRho= 0.0
    # d_lnfree_e_dlnT= 0.0
    
    use_Zbase_for_Type1 = False
    frac_Type2 = 1.0
    kap = 0.0
    dlnkap_dlnRho = 0.0
    dlnkap_dlnT = 0.0
    ierr = 0
    
    # res = kap_lib.kap_get_Type2( 
            # handle, zbar, X, Z, Zbase, XC, XN, XO, XNe, logRho, logT, 
            # lnfree_e, d_lnfree_e_dlnRho, d_lnfree_e_dlnT, use_Zbase_for_Type1, 
            # frac_Type2, kap, dlnkap_dlnRho, dlnkap_dlnT, ierr)
        
    res = kap_lib.kap_get_Type1( 
            handle, zbar, X, Z, logRho, logT, 
            lnfree_e, d_lnfree_e_dlnRho, d_lnfree_e_dlnT, 
            kap, dlnkap_dlnRho, dlnkap_dlnT, ierr)
        
    # print(res)
    if not deriv:
        answer = np.log(res['kap'])
    else:
        if test_var is 't':
            answer = res['dlnkap_dlnt']
        elif test_var is 'r':
            answer = res['dlnkap_dlnrho']
        
        
    return answer


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
        if r[1] != 0.0:
            err.append(np.abs(r[2]/r[1]))
        else:
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
    
def plot2d(xmin,xmax,ymin,ymax,xsteps,ysteps,deriv_flag,name,rev=False,title=''):    
    
    xvalues=np.linspace(xmin,xmax,int(xsteps))
    yvalues=np.linspace(ymin,ymax,int(ysteps))
    
    z=[]
    
    for i in xvalues:
        z.append([])
        for j in yvalues:
            #print(i,j)
            r=bestfit(i,deriv_flag,j)
            z[-1].append(np.log10(np.abs(r[3])))
    
    z=np.array(z)
    fig=plt.figure()
    ax=fig.add_subplot(111)
    
    extent=(xmin,xmax,ymin,ymax)
    if rev:
        z=z.T
        extent=(ymin,ymax,xmin,xmax)
    
    cax=ax.imshow(z.T,extent=extent,aspect='auto',vmin=np.maximum(np.min(z),-16.0),vmax=0.0,origin='lower')
    cb=fig.colorbar(cax)
    
    cb.set_label('log abs dfriddr err')
    ax.set_title(title)
    ax.set_xlabel('lnT')
    ax.set_ylabel('LnRho')
    fig.savefig(name)
    plt.close(fig)
    
mod="kap"


pym.buildModule(mod)

const_lib, const_def = pym.loadMod("const")
crlibm_lib, _ = pym.loadMod("crlibm")
chem_lib, chem_def = pym.loadMod("chem")
kap_lib,kap_def = pym.loadMod("kap")

ierr=0

crlibm_lib.crlibm_init()
const_lib.const_init(pym.MESA_DIR,ierr)
chem_lib.chem_init('isotopes.data',ierr)


kap_lib.kap_init('gs98','gs98_co','lowT_fa05_gs98',3.88,3.80,3.80,False,pym.KAP_CACHE,'',ierr)

kap_handle = kap_lib.alloc_kap_handle(ierr)

kap_lib.kap_set_choices(kap_handle,False,False,True,0.71,0.70,0.001,0.01,ierr)



# eval_x(9.0,'t',9.0,deriv=True)

prefix=sys.argv[1]

steps=200

#ln values
tmin=0.0
tmax=10.0
rmin=0.0
rmax=10.0

j='t'
#dt term
# minT maxT minRho maxRho
plot2d(tmin,tmax,rmin,rmax,steps,steps,j,prefix+'_'+j+'_all.pdf',title='dt')


j='r'
#drho term
# minRho maxRho minT maxT
plot2d(rmin,rmax,tmin,tmax,steps,steps,j,prefix+'_'+j+'_all.pdf',rev=True,title='drho')

