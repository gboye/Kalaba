
# coding: utf-8

# In[18]:


from os.path import expanduser
home = expanduser("~")
repertoire=home+"/Copy/Cours/Bordeaux/L1-UE1/Kalaba-14"
serie=repertoire+"/"
#########################IMPORTS############################################
import codecs, optparse
import re, random
import sys,os,time
import string
import yaml
import ParFuMor as PFM
from ParFuMor import *
import pickle


# In[19]:

print_glose=False
print_cloze=True
#numeros={'1':'Un','2':'Deux','3':'Trois','4':'Quatre','5':'Cinq'}


# In[20]:

with open(serie+"Phonology.yaml", 'r') as stream:
    phonology=yaml.load(stream)
with open(serie+"MorphoSyntax.yaml", 'r') as stream:
    morphosyntax=yaml.load(stream)
with open(serie+"Hierarchie.pkl", 'rb') as input:
   PFM.hierarchieCF = pickle.load(input)
with open(serie+"Lexique.pkl", 'rb') as input:
   PFM.lexique = pickle.load(input)
with open(serie+"Regles.pkl", 'rb') as input:
   PFM.regles = pickle.load(input)


# ####Définition des segments

# In[21]:

consonnes=phonology["consonnes"]
voyelles=phonology["voyelles"]
gabarits=phonology["gabarits"]
derives=phonology["derives"]
nom_classe=phonology["nom_classe"]
nom_apo=phonology["apophonies"]
nom_mut=phonology["mutations"]
syllabes=phonology["syllabes"]


# ####Attention aux correspondances pour les syllabes
# YAML interprète la clé no comme False

# In[22]:

def parse_grapho(graphie):
#    chunks=re.findall(r"([ptkbdgmnNfsSvzjrlyv]?[aeiou]?)|[aeiou]|[ptkbdgmnNfsSvzjrlyv]|[.…,;!?:—–()\[\]\/# ""«»<>]", graphie)
    chunks=re.findall(r"([ptkbdgmnNfsSvzjrlyv]?[aeiou]?)|[.…,;!?:—–()\[\]\/# ""«»<>]", graphie)
    result=[]
    for chunk in chunks:
#        print [chunk],syllabes.keys()
        if chunk in syllabes.keys():
            result.append(syllabes[chunk])
        else:
            result.append(chunk)
    return "".join(result)


# In[23]:

def parse_cloze(glose):
    chunks=re.findall(r"\\cacherGloses{([^}]*)?}|(\w+)", glose.decode('utf8'),re.UNICODE)
    result=[]
    for chunk in chunks:
        result.extend([x.encode('utf8') for x in chunk if x!=""])
    return "%s;"%len(result)+";".join(result)


# In[24]:

#grapho=recoder("SviNaNeNNoNN",translit)
#grapho,parse_grapho(grapho)


# In[25]:

try:
    __IPYTHON__ 
    ipython=True
except: 
    ipython=False

version=os.path.basename("__file__")
time_stamp='%s' % time.strftime("%y%m%d-%H%M")
print "%% version : "+version
print "%% traitement : "+time_stamp

if ipython or True:
#    lexeme_nom="lexemes.txt"
#    phrase_nom="phrases.txt"
    pass
else:
    parser=optparse.OptionParser()
    parser.add_option("-o", "--out", dest="outfile", action="store_true", help="write to FILE")
    parser.add_option("-c", "--cloze", dest="print_cloze", action="store_true", help="write a CLOZE FILE")
    parser.add_option("-l", "--lexicon", dest="print_lexique", action="store_true", help="append a lexicon")
    parser.add_option("-r", "--roots", dest="print_racines", action="store_true", help="append a root list")

    (options, args) = parser.parse_args()
    lexeme_nom=args[0]
    phrase_nom=args[1]


# In[26]:

def recoder(chaine,table):
    if type(chaine)==str:
        temp=unicode(chaine.decode('utf8')).translate(table)
        result=temp.encode('utf8')
    elif type(chaine)==unicode:
        result=chaine.translate(table)
    return result
#translit=string.maketrans(u'iueoaftgzZvjkSpN',u'tgazpHTGZJVkXyxI')
phonoIn =  unicode(phonology["translations"]["grapho"]["in"])
graphoIn = [ord(char) for char in phonoIn]
graphoOut = unicode(phonology["translations"]["grapho"]["out"])
translit = dict(zip(graphoIn, graphoOut))


# In[27]:

accentedIn = unicode(phonology["translations"]["deaccent"]["in"])
deaccentIn = [ord(char) for char in accentedIn]
deaccentOut = unicode(phonology["translations"]["deaccent"]["out"])
deaccent = dict(zip(deaccentIn, deaccentOut))


# In[28]:

tipaIn = unicode(phonology["translations"]["ipa"]["in"])
ipaIn = [ord(char) for char in tipaIn]
ipaOut = unicode(phonology["translations"]["ipa"]["out"])
toipa = dict(zip(ipaIn, ipaOut))


# In[29]:

tableaux={}
gloseClozes={}
declarations=[]
for categorie in PFM.lexique.catLexeme:
    if not categorie in tableaux:
        tableaux[categorie]=[]
        gloseClozes[categorie]=[]
    if verbose: print categorie
    for lexeme in PFM.lexique.catLexeme[categorie]:
        if verbose: print PFM.lexique.lexemes[lexeme]
        for case in PFM.lexique.lexemes[lexeme].paradigme.cases:
            if categorie in PFM.categoriesMajeures:
                nom=PFM.lexique.lexemes[lexeme].nom
            else:
                nom=PFM.lexique.lexemes[lexeme].nom.upper()
            ref=PFM.modifierGlose(nom,case.sigma,"ref")
            ref=recoder(ref,deaccent)
#            for num in numeros:
#                ref=ref.replace(num,numeros[num])
            phono=case.forme
            grapho=parse_grapho(recoder(phono,translit))
            declarations.append("\\newcommand{\\"+ref+"}{\\strutgb{0pt}\\grapho{"+grapho+"}}")
            declarations.append("\\newcommand{\\"+ref+"P}{\\textipa{"+case.forme+"}}")
            declarations.append("\\newcommand{\\"+ref+"G}{"+case.glose+"}")
            if print_glose:
                tableaux[categorie].append("\\"+ref+" & \\"+ref+"P & \\"+ref+"G \\\\")
            else:
                tableaux[categorie].append("\\"+ref+" & \\"+ref+"P & \\\\")
            if print_cloze:
                vedette=nom.split(".")[0]
                gloses=parse_cloze(case.glose)
                try:
                    cloze=";".join([vedette,categorie,phono,case.decoupe,case.sigma,gloses])
                except NameError:
                    cloze=";".join([vedette,categorie,phono,gloses])
                gloseClozes[categorie].append(cloze)
    


# In[30]:

with open(serie+"Declarations.tex", 'wb') as output:
    for declaration in declarations:
        output.write(declaration+"\n")


# In[31]:

with open(serie+"Clozes.txt", 'wb') as output:
    for categorie in gloseClozes:
        output.write("#\t"+categorie+"\n#\n#\n")
        for cloze in gloseClozes[categorie]:
            output.write(cloze+"\n")
        output.write("#\n#\n#\n")


# In[32]:

with open(serie+"Tableaux.yaml", 'w') as outfile:
    outfile.write(yaml.dump(tableaux, default_flow_style=True))


# In[33]:

gloseClozes


# In[34]:

parse_cloze("\cacherGloses{PST-}donner\cacherGloses{.VD.V2}\cacherGloses{-D}")


# In[34]:



