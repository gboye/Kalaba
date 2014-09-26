
# coding: utf-8

# #ParFuMor (version YAML & Objets)

# In[1]:


from os.path import expanduser
home = expanduser("~")
repertoire=home+"/Copy/Cours/Bordeaux/L1-UE1/Kalaba-14"
serie=repertoire+"/"

import yaml
import itertools
#import re
import ParFuMor as PFM
from ParFuMor import *
import pickle


# In[2]:

with open(serie+"Gloses.yaml", 'r') as stream:
    gloses=yaml.load(stream)
    PFM.gloses=gloses
with open(serie+"Stems.yaml", 'r') as stream:
    stems=yaml.load(stream)
    PFM.stems=stems
with open(serie+"Blocks.yaml", 'r') as stream:
    blocks=yaml.load(stream)
    PFM.blocks=blocks
with open(serie+"Phonology.yaml", 'r') as stream:
    phonology=yaml.load(stream)
    PFM.phonology=phonology
with open(serie+"MorphoSyntax.yaml", 'r') as stream:
    morphosyntax=yaml.load(stream)
    PFM.morphosyntax=morphosyntax


# In[3]:

regles=Regles()
PFM.regles=regles
for categorie in blocks:
    regles.addBlocs(categorie,blocks[categorie])


# In[4]:

paradigmes=Paradigmes()
PFM.paradigmes=paradigmes


# In[5]:

hierarchieCF=HierarchieCF()
PFM.hierarchieCF=hierarchieCF
lexique=Lexique()
PFM.lexique=lexique


# In[6]:

paradigmes=Paradigmes()
PFM.paradigmes=paradigmes


# In[7]:

paradigmes=Paradigmes()
PFM.paradigmes=paradigmes
for cat in gloses:
#    print cat
    attributes=[]
    if gloses[cat]:
        if set(gloses[cat].keys())==set(morphosyntax["Attributs"][cat]):
            features=morphosyntax["Attributs"][cat]
#            print "inhérent",features
        else:
            features=gloses[cat].keys()
#            print "contextuel",features
        for attribute in features:
            attributes.append(gloses[cat][attribute])
        nuplets=(itertools.product(*attributes))
        for nuplet in nuplets:
            proprietes=[cat]
            for element in range(len(nuplet)):
                proprietes.append("%s=%s"%(features[element],nuplet[element]))
            paradigmes.addForme(cat,proprietes)


# In[8]:

analyserGloses(gloses)
analyserStems(stems)


# In[9]:

with open(serie+"Hierarchie.pkl", 'wb') as output:
   pickle.dump(hierarchieCF, output, pickle.HIGHEST_PROTOCOL)
with open(serie+"Lexique.pkl", 'wb') as output:
   pickle.dump(lexique, output, pickle.HIGHEST_PROTOCOL)
with open(serie+"Regles.pkl", 'wb') as output:
   pickle.dump(regles, output, pickle.HIGHEST_PROTOCOL)

