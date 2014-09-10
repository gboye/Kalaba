# coding: utf-8

# #ParFuMor (version YAML & Objets)

# In[1]:

import yaml
import itertools
#import re
import ParFuMor
from ParFuMor import *
import pickle


# In[2]:

with open("Kalaba-Gloses.yaml", 'r') as stream:
    gloses=yaml.load(stream)
    ParFuMor.gloses=gloses
with open("Kalaba-Stems.yaml", 'r') as stream:
    stems=yaml.load(stream)
    ParFuMor.stems=stems
with open("Kalaba-Blocks.yaml", 'r') as stream:
    blocks=yaml.load(stream)
    ParFuMor.blocks=blocks


# In[3]:

regles=Regles()
ParFuMor.regles=regles
for categorie in blocks:
    regles.addBlocs(categorie,blocks[categorie])


# In[4]:

paradigmes=Paradigmes()
ParFuMor.paradigmes=paradigmes
for cat in gloses:
    attributes=[]
    if gloses[cat]:
        for attribute in gloses[cat]:
            attributes.append(gloses[cat][attribute])
        nuplets=(itertools.product(*attributes))
        for nuplet in nuplets:
            proprietes=[cat]
            for element in range(len(nuplet)):
                proprietes.append("%s=%s"%(gloses[cat].keys()[element],nuplet[element]))
            paradigmes.addForme(cat,proprietes)


# In[5]:

hierarchieCF=HierarchieCF()
ParFuMor.hierarchieCF=hierarchieCF
lexique=Lexique()
ParFuMor.lexique=lexique


# In[6]:

analyserStems(stems)


# In[ ]:

with open('Hierarchie.pkl', 'wb') as output:
   pickle.dump(hierarchieCF, output, pickle.HIGHEST_PROTOCOL)
with open('Lexique.pkl', 'wb') as output:
   pickle.dump(lexique, output, pickle.HIGHEST_PROTOCOL)
with open('Regles.pkl', 'wb') as output:
   pickle.dump(regles, output, pickle.HIGHEST_PROTOCOL)


# In[ ]:

lexique.getLexemes("e")


# In[11]:

hierarchieCF.trait


# In[ ]:



