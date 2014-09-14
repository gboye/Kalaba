
# coding: utf-8

# In[1]:



#########################IMPORTS############################################
import codecs, optparse
import re, random
import sys,os,time
import string
import yaml
import ParFuMor as PFM
from ParFuMor import *
import pickle


# In[2]:

print_glose=True
numeros={'1':'Un','2':'Deux','3':'Trois','4':'Quatre','5':'Cinq'}


# In[3]:

with open("Kalaba-Phonology.yaml", 'r') as stream:
    phonology=yaml.load(stream)
with open("Kalaba-MorphoSyntax.yaml", 'r') as stream:
    morphosyntax=yaml.load(stream)
with open('PFM-Hierarchie.pkl', 'rb') as input:
   PFM.hierarchieCF = pickle.load(input)
with open('PFM-Lexique.pkl', 'rb') as input:
   PFM.lexique = pickle.load(input)
with open('PFM-Regles.pkl', 'rb') as input:
   PFM.regles = pickle.load(input)


# ####Définition des segments

# In[4]:

consonnes=phonology["consonnes"]
voyelles=phonology["voyelles"]
gabarits=phonology["gabarits"]
derives=phonology["derives"]
nom_classe=phonology["nom_classe"]
nom_apo=phonology["apophonies"]
nom_mut=phonology["mutations"]
syllabes=phonology["syllabes"]


# In[5]:

def parse_grapho(graphie):
    chunks=re.findall(r"([djkmnpqrstwz][aeiou]?)|[aeiou]|[.…,;!?:—–()\[\]\/# ""«»<>]", graphie)
    result=[]
    for chunk in chunks:
        if chunk in syllabes.keys():
            result.append(syllabes[chunk])
        else:
            result.append(chunk)
    return "".join(result)


# In[6]:

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
    lexeme_nom="lexemes.txt"
    phrase_nom="phrases.txt"
else:
    parser=optparse.OptionParser()
    parser.add_option("-o", "--out", dest="outfile", action="store_true", help="write to FILE")
    parser.add_option("-c", "--cloze", dest="print_cloze", action="store_true", help="write a CLOZE FILE")
    parser.add_option("-l", "--lexicon", dest="print_lexique", action="store_true", help="append a lexicon")
    parser.add_option("-r", "--roots", dest="print_racines", action="store_true", help="append a root list")

    (options, args) = parser.parse_args()
    lexeme_nom=args[0]
    phrase_nom=args[1]


# In[7]:

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


# In[8]:

accentedIn = unicode(phonology["translations"]["deaccent"]["in"])
deaccentIn = [ord(char) for char in accentedIn]
deaccentOut = unicode(phonology["translations"]["deaccent"]["out"])
deaccent = dict(zip(deaccentIn, deaccentOut))


# In[9]:

tipaIn = unicode(phonology["translations"]["ipa"]["in"])
ipaIn = [ord(char) for char in tipaIn]
ipaOut = unicode(phonology["translations"]["ipa"]["out"])
toipa = dict(zip(ipaIn, ipaOut))


# In[10]:

tableaux={}
for categorie in PFM.lexique.catLexeme:
    if not categorie in tableaux:
        tableaux[categorie]=[]
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
            for num in numeros:
                ref=ref.replace(num,numeros[num])
            phono=case.forme
            grapho=parse_grapho(recoder(phono,translit))
            print "\\newcommand{\\"+ref+"}{\\strutgb{0pt}\\grapho{"+grapho+"}}"
            print "\\newcommand{\\"+ref+"P}{\\textipa{"+case.forme+"}}"
            print "\\newcommand{\\"+ref+"G}{"+case.glose+"}"
            if print_glose:
                tableaux[categorie].append("\\"+ref+" & \\"+ref+"P & \\"+ref+"G \\\\")
            else:
                tableaux[categorie].append("\\"+ref+" & \\"+ref+"P & \\\\")
    


# In[10]:



