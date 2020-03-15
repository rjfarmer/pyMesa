import pymesa as pm

p=pm.mesa('./mesa','./mesasdk')

c=pm.const.const(p.defaults)
print(c.const_lib.amu)

a=pm.atm.atm(p.defaults)
print(a.atm_Teff(1.0,1.0))

# Skip as broken at the moment
#colors=pm.colors.colors(p.defaults)
#print(colors.get_bc('V',5.0,4.5,0.0))

c=pm.chem.chem(p.defaults)
print(c.basic_composition_info({'h1':0.5,'he4':0.5}))
print(c.chem_lib.chem_get_element_id('h1'))


e=pm.eos.eos(p.defaults)
print(e.eos_def.i_lnPgas)
print(e.getEosDT({'h1':0.5,'he4':0.5},10**7,10**4))


ion=pm.ion.ion(p.defaults)
print(ion.getIon(10**5,10**2,0.02,0.75))

kap=pm.kap.kap(p.defaults)
comp = c.basic_composition_info({'h1':0.5,'he4':0.25,'c12':0.25})

print(kap.kap_get(comp['zbar'],comp['xh'],comp['z'],comp['z'],0.25,0.0,0.0,0.0,
        3.0,7.0,0.0,0.0,0.0))



import pymesa as pm 
p=pm.mesa('./mesa','./mesasdk')
defaults = p.defaults
s = pm.star.star(p.defaults)
