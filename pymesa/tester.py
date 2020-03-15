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



