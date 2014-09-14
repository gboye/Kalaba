
# coding: utf-8

# #ParFuMor (version YAML & Objets)

# In[1]:

import yaml
import itertools
#import re
import ParFuMor as PFM
from ParFuMor import *
import pickle


# In[2]:

with open("Kalaba-Gloses.yaml", 'r') as stream:
    gloses=yaml.load(stream)
    PFM.gloses=gloses
with open("Kalaba-Stems.yaml", 'r') as stream:
    stems=yaml.load(stream)
    PFM.stems=stems
with open("Kalaba-Blocks.yaml", 'r') as stream:
    blocks=yaml.load(stream)
    PFM.blocks=blocks
with open("Kalaba-Phonology.yaml", 'r') as stream:
    phonology=yaml.load(stream)
    PFM.phonology=phonology
with open("Kalaba-MorphoSyntax.yaml", 'r') as stream:
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
for cat in gloses:
    attributes=[]
    if gloses[cat]:
        if set(gloses[cat].keys())==set(morphosyntax["Attributs"][cat]):
            features=morphosyntax["Attributs"][cat]
        else:
            features=gloses[cat].keys()
        for attribute in features:
            attributes.append(gloses[cat][attribute])
        nuplets=(itertools.product(*attributes))
        for nuplet in nuplets:
            proprietes=[cat]
            for element in range(len(nuplet)):
                proprietes.append("%s=%s"%(features[element],nuplet[element]))
            paradigmes.addForme(cat,proprietes)

# In[5]:

hierarchieCF=HierarchieCF()
PFM.hierarchieCF=hierarchieCF
lexique=Lexique()
PFM.lexique=lexique


# In[6]:

analyserGloses(gloses)
analyserStems(stems)


# In[7]:

hierarchieCF.trait


# In[8]:

paradigmes.getSigmas("M")


# In[9]:

with open('PFM-Hierarchie.pkl', 'wb') as output:
   pickle.dump(hierarchieCF, output, pickle.HIGHEST_PROTOCOL)
with open('PFM-Lexique.pkl', 'wb') as output:
   pickle.dump(lexique, output, pickle.HIGHEST_PROTOCOL)
with open('PFM-Regles.pkl', 'wb') as output:
   pickle.dump(regles, output, pickle.HIGHEST_PROTOCOL)


# In[10]:

lexique.getLexemes("dans")[0].classe in PFM.categoriesMineures


# In[11]:

lexique.catLexeme


# In[12]:

lexique.getLexemes("dormir")[0]


# In[13]:

mot="café"
type(mot),lexique.formeLexeme[mot]


# In[13]:



