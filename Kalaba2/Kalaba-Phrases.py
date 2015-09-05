
# coding: utf-8

# In[2531]:


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


# In[2532]:

#########################VARIABLES##########################################
version=os.path.basename("__file__")
time_stamp='%s' % time.strftime("%y%m%d-%H%M")
debug=0
debug_now=0
print_no=False
print_taches=True
print_coffee=True
print_commands=True
print_phrases=True
print_glose=False
print_lexique=True
print_cloze=False
print_racines=False
no_form="***"
# no_grapho=['dormir', 'lit']
# no_phono=['gros', 'coussin']
no_grapho=['petit','Nabil',"sur"]
no_phono=["grand","autruche",'dans']
phono_no=u"XXXXX"
grapho_no=u"XXXXX"


# In[2533]:

with open(serie+"Gloses.yaml", 'r') as stream:
    gloses=yaml.load(stream)
with open(serie+"Phonology.yaml", 'r') as stream:
    phonology=yaml.load(stream)
with open(serie+"MorphoSyntax.yaml", 'r') as stream:
    morphosyntax=yaml.load(stream)
with open(serie+"Tableaux.yaml", 'r') as stream:
    tableaux=yaml.load(stream)
with open(serie+"Hierarchie.pkl", 'rb') as input:
   PFM.hierarchieCF = pickle.load(input)
with open(serie+"Lexique.pkl", 'rb') as input:
   PFM.lexique = pickle.load(input)
with open(serie+"Regles.pkl", 'rb') as input:
   PFM.regles = pickle.load(input)


# ####Définition des entêtes

# In[2534]:

#########################CONSTANTS##########################################
head = [
"\\begin{tabular}[t]{|l|l|l|}",
"\\addlinespace[-1.0em]\\hline",
"Mot & Roman & Glose  \\\\",
"\\hline\\strutgh{14pt}%"
]
head_n = [
"\\begin{tabular}[t]{|l|c|c|c|}",
"\\addlinespace[-1.0em]\\hline",
"Nom & Genre & C\\indice{1}C\\indice{2}C\\indice{3} & V\\indice{L}  \\\\",
"\\hline\\strutgh{14pt}%"
]
head_v = [
"\\begin{tabular}[t]{|l|c|c|}",
"\\addlinespace[-1.0em]\\hline",
"Verbe & Type & C\\indice{1}C\\indice{2}C\\indice{3} \\\\",
"\\hline\\strutgh{14pt}%"
]


# In[2535]:

tail = [
"\\hline"
"\\end{tabular}\\\\"
]


# ####Définition des structures pour impression

# In[2536]:

exemples=[]
accumulateur=[]
vocabulaire=[]
def accumulerMots(mot):
    accumulateur.append(mot)
    return
def ajouterExemple(exemple,printBool=False):
    if printBool:
        print exemple
    exemples.append(exemple.strip())
    del accumulateur[:]
    return
def ajouterVocabulaire(terme,printBool=False):
    if printBool:
        print terme
    vocabulaire.append(terme.strip())
    return


# ####Définition des segments

# In[2537]:

consonnes=phonology["consonnes"]
voyelles=phonology["voyelles"]
gabarits=phonology["gabarits"]
derives=phonology["derives"]
nom_classe=phonology["nom_classe"]
nom_apo=phonology["apophonies"]

nom_mut=phonology["mutations"]


# ####Définition des catégories

# In[2538]:

genres=gloses["N"]["Genre"]
types=gloses["V"]["Type"]
i=2
verbe_forme={}
for forme in morphosyntax["V"]["FormesBase"]:
    verbe_forme[i]=forme
    i+=1


# In[2539]:

def recoder(chaine,table):
    if type(chaine)==str:
        temp=unicode(chaine.decode('utf8')).translate(table)
        result=temp.encode('utf8')
    elif type(chaine)==unicode:
        result=chaine.translate(table)
    return result

accentedIn = unicode(phonology["translations"]["deaccent"]["in"])
deaccentIn = [ord(char) for char in accentedIn]
deaccentOut = unicode(phonology["translations"]["deaccent"]["out"])
deaccent = dict(zip(deaccentIn, deaccentOut))


# In[2540]:

syntagmes=morphosyntax["Syntagmes"]


# In[2541]:

contractions=morphosyntax["Contractions"]
for contraction in contractions:
    temp=[]
    for element in contractions[contraction]:
        if isinstance(element,unicode):
            temp.append(element.encode("utf8"))
        else:
            temp.append(element)
    contractions[contraction]=temp


# In[2542]:

syllabes=phonology["syllabes"]


# In[2543]:

def taches():
    def makeStain():
        seed=random.randint(1,1000)
        x=random.gauss(11,5)-2
        y=random.gauss(2,1)
        minimum=random.gauss(.2,.1)+.1
        maximum=random.gauss(.1,.05)+.5
        return "\\taches{%s}{%s}{%s}{%s}{%s}"%(seed,x,y,minimum,maximum)

    if print_taches:
        n=random.gauss(10,2.5)
        if n<8:
            return ""
        elif n<16:
            return makeStain()
        else:
            nTaches=int(n-15)
            stains=""
            for i in range(nTaches):
                stains+=makeStain()
            return stains
    else:
        return ""


# In[2544]:

def faire_tableau(tableau,tab=(head,tail,"")):
    if len(tableau)==0: return
    comment=tab[2]
    for element in tab[0]:
        ajouterVocabulaire(comment+element)
    for element in tableau:
        ajouterVocabulaire(comment+element)
    for element in tab[1]:
        ajouterVocabulaire(comment+element)


# In[2545]:

def print_tableaux(cols,tableau,texte="",debut=0,tab=(head,tail,"")):
    ajouterVocabulaire(tab[2]+"\\begin{multicols}{"+str(cols)+"}")
    if texte!="":
        table=filtrer_tableau(tableau,texte)
    else:
        table=tableau
    chunk=(len(table)-debut*cols)/cols+1
    faire_tableaux(table,debut,cols,tab)
    ajouterVocabulaire(tab[2]+"\\end{multicols}")


# In[2546]:

def faire_tableaux(tableau,debut=16,nombre=1,tab=(head,tail,"")):
    reste=[]
    if debug: print nombre,debut,tableau
    if debut!=0:
        for i in range(nombre):
            faire_tableau(tableau[debut*i:debut*(i+1)],tab)
        table=tableau[debut*nombre:]
    else:
        table=tableau
    longueur=len(table)
    chunk=longueur/nombre+1
    if debug: print "CHUNKING : ",longueur, nombre, chunk, table
    if chunk<48:
        chunks=chunk
    else:
        chunks=48
        reste=table[48*nombre:]
    if debug: print "RESTE : ", chunk, reste
    for i in range(nombre):
        faire_tableau(table[chunks*i:chunks*(i+1)],tab)
    if reste:
        faire_tableaux(reste,0,nombre,tab)


# In[2547]:

def filtrer_tableau(tableau,filtre):
    result=[]
    for line in tableau:
        elements=line.split(" ")
        if elements[0] in filtre: result.append(line)
    return result


# In[2548]:

def faire_gn(depart,cas):
    global erg_genre, erg_nombre, abs_genre, abs_nombre
    if debug: print "groupe depart :", depart
    groupe_nom=[]
    groupe_nom.append(depart[0])
    if debug: print depart[0]
    for mot in depart[1:]:
        if debug: print mot
        groupe_nom.extend(etendre_contraction([mot]))
    if debug: print "groupe nom :", groupe_nom
    mots=[]
    det=[]
    adj=[]
    nom=[]
    gp=[]
    tete=""
    nombre=""
    reste=0
    for mot in groupe_nom:
        if reste==0:
            if mot=="deux":
                nombre="DU"
                if det==[]: det.append(PFM.lexique.formeLexeme["des"][0])
            else:
                nomLexeme=PFM.lexique.formeLexeme[mot][0]
                categorie=PFM.lexique.lexemes[nomLexeme].classe.split(".")[-1]
                if debug: 
                    print "mot",[mot]
                    print "vedette",PFM.lexique.formeLexeme[mot][0],categorie
                    print "categories",PFM.hierarchieCF.classes["N"],PFM.hierarchieCF.getCategory(categorie)
                if PFM.hierarchieCF.getCategory(categorie)=="N":
                    tete=categorie
                    if debug: print "tête :", tete
                    tampon=tete.split('.')
                    classe=tampon[0]
                    try:
                        typeMot=tampon[1]
                    except IndexError:
                        typeMot=''
                    if mot[len(mot)-1]=='s':
                        if nombre=="": nombre="PL"
                    else:
                        if nombre=="": nombre="SG"
                    nom.append(PFM.lexique.formeLexeme[mot][0])
                    cellule=classe.capitalize()+nombre.capitalize()+cas.capitalize()
                    if cas=="ERG":
                        erg_genre=classe
                        erg_nombre=nombre
                    elif cas=="ABS":
                        abs_genre=classe
                        abs_nombre=nombre
                elif categorie in ["DET"]:
                    det.append(PFM.lexique.formeLexeme[mot][0])
                elif categorie in PFM.hierarchieCF.classes["ADJ"]:
                    adj.append(PFM.lexique.formeLexeme[mot][0])
                elif categorie=="PREP":			#Si on trouve une PREP, elle et le reste forment un GP
                    gp.append(mot)
                    reste=1
        else:							#On a trouvé une PREP, toute la suite va dans DP
            gp.append(mot)
    if debug: print "accord :", tete
    if reste==1: gp=faire_gp(gp)
    if debug: print "GP dans le GN : ", gp
    if debug: print "GN sans det ? ", det
    if not det: det.append("IND")
    for mot in det:
#		glose=faire_glose(mot,classe,type,nombre)
        ref="\\"+recoder(mot.split(".")[0],deaccent).upper()+nombre.capitalize()+cas.capitalize()
        mots.append(ref)
        texte.append(ref)
    for mot in gp: mots.append(mot)
    for mot in adj:
#		glose=faire_glose(mot,classe,type,nombre)
        ref="\\"+recoder(mot.split(".")[0],deaccent).lower()+classe.capitalize()+nombre.capitalize()
        mots.append(ref)
        texte.append(ref)
    for mot in nom:
#		glose=faire_glose(mot,classe,type,nombre)
        if mot.istitle():
            ref="\\"+recoder(mot.split(".")[0],deaccent)+cellule
        else:
            ref="\\"+recoder(mot.split(".")[0],deaccent).lower()+cellule
        mots.append(ref)
        texte.append(ref)
    return mots


# In[2549]:

def faire_gp(groupe_prep):
    mots=[]
    groupe_prep=etendre_contraction(groupe_prep)
    if debug: print "faire_gp", groupe_prep
    preposition=groupe_prep[0]
    if preposition!="à" :
        if debug: print "PREP!=à",[groupe_prep[0],"à"]
        ref="\\"+recoder(groupe_prep[0],deaccent).upper()
        mots.append(ref)
        texte.append(ref)
        if debug:
            print "groupe prep :", groupe_prep
            print ref
        if len(groupe_prep)>1:
            groupe_nom=groupe_prep[1:]
            mots.insert(0,faire_gn(groupe_nom,"OBL"))
        return mots
    else:
        groupe_nom=groupe_prep[1:]
        if debug: print "faire_gn", groupe_nom, faire_gn(groupe_nom,"DAT")
        mots.append(faire_gn(groupe_nom,"DAT"))
        return mots


# In[2550]:

def etendre_contraction(liste):
    result=[]
    if liste[0] in contractions.keys():
        if debug: print "EXT : ", liste, contractions[liste[0]],liste[1:] 
        result.extend(contractions[liste[0]])
        result.extend(liste[1:])
    else:
        result=liste
    return result


# In[2551]:

def printflat(liste,suffixe="",prefixe=""):
    if debug: print "printflat", liste
    if not isinstance(liste, basestring):
        for element in liste:
            accumulerMots(prefixe)
            printflat(element,suffixe)
    else: 
        accumulerMots(prefixe)
        accumulerMots(liste+suffixe)


# In[2552]:

#######################
#
#	INITIALISATION DES VARIABLES
#
#######################

try:
    __IPYTHON__ 
    ipython=True
except: 
    ipython=False


# In[2553]:

################
#
# LECTURE DU FICHIER DE LEXEMES
#
#		LES LIGNES QUI COMMENCENT PAR # SONT IGNOREES
#
################
print "%% version : "+version
print "%% traitement : "+time_stamp

if ipython or True:
#    lexeme_nom=serie+"Lexemes.txt"
    phrase_nom=serie+"Phrases.txt"
else:
    parser=optparse.OptionParser()
    parser.add_option("-o", "--out", dest="outfile", action="store_true", help="write to FILE")
    parser.add_option("-c", "--cloze", dest="print_cloze", action="store_true", help="write a CLOZE FILE")
    parser.add_option("-l", "--lexicon", dest="print_lexique", action="store_true", help="append a lexicon")
    parser.add_option("-r", "--roots", dest="print_racines", action="store_true", help="append a root list")

    (options, args) = parser.parse_args()
    lexeme_nom=args[0]
    phrase_nom=args[1]


# ####Ouverture du fichier lexique

# ####Ouverture du fichier phrases

# In[2554]:

try:
    phrase_file = codecs.open(phrase_nom,"r","utf-8")
except IOError:
    print 'I could not open the sentence file', phrase_nom
    sys.exit()


# In[2555]:

def recoder(chaine,table):
    if type(chaine)==str:
        temp=unicode(chaine.decode('utf8')).translate(table)
        result=temp.encode('utf8')
    elif type(chaine)==unicode:
        result=chaine.translate(table)
    return result


# In[2556]:

accentedIn = unicode(phonology["translations"]["deaccent"]["in"])
deaccentIn = [ord(char) for char in accentedIn]
deaccentOut = unicode(phonology["translations"]["deaccent"]["out"])
deaccent = dict(zip(deaccentIn, deaccentOut))


# In[2557]:

tipaIn = unicode(phonology["translations"]["ipa"]["in"])
ipaIn = [ord(char) for char in tipaIn]
ipaOut = unicode(phonology["translations"]["ipa"]["out"])
toipa = dict(zip(ipaIn, ipaOut))


# In[2558]:

#################################################
#################################################
#################################################
##
##
##	FAIRE LE TRI DES FORMES UTILISEES DANS LES PHRASES
##	AFFICHER DANS LES TABLEAUX SEULEMENT CES FORMES
##
##
#################################################
################################################
#
#
#	FAIRE LA LISTE DES PHRASES AVEC LES 4 LIGNES
#		GRAPHO, PHONO, GLOSE, TRAD
#
#
################################################
texte=[]
#graphies={}
#abs_genre=""
#abs_nombre=""


# In[2559]:

if print_phrases:
    comment=""
else:
    comment="%"
ajouterExemple(comment+"\\begin{exe}")
for line in phrase_file:
    phrase=[0 for i in range(len(syntagmes['Phrase']))]
    tampon=(line.strip().rstrip('.')).replace("'"," ").encode("utf8").split("\t")
    if not tampon[0].startswith("#"):
        verbe=tampon[1].split(" ")
        verbeForme=verbe[0]
        if len(PFM.lexique.formeLexeme[verbeForme])!=1:
            print "FORME AMBIGUË"
        verbeLexeme=PFM.lexique.formeLexeme[verbeForme][0]
        temp=verbeLexeme.split(".")
        formeCitation=temp[0]
        typeVerbe=temp[1]
#        print verbeLexeme, formeCitation,typeVerbe
        verbeLemme="%s%s"%(formeCitation,typeVerbe.capitalize())
        verbeFormeIndex=PFM.lexique.lexemes[verbeLexeme].formes.index(verbeForme)
        if debug: print "verbe :", verbe
        if verbeLexeme.endswith("VI"):
            suj_cas="ABS"
        else:
            suj_cas="ERG"
            obj_cas="ABS"
        suj_genre="A"
        suj_nombre="SG"
        obj_genre="A"
        obj_nombre="SG"
        sujet=tampon[0].strip().split(" ")
        phrase[syntagmes['Phrase'].index('SUJ')]=faire_gn(sujet,suj_cas)
        if debug: print "sujet :",phrase[1]
        if len(tampon)>=3:
            objet=tampon[2].split(" ")
            if debug: print "objet : ",objet
            if objet!=['']: phrase[syntagmes['Phrase'].index('OBJ')]=faire_gn(objet,obj_cas)
        if len(tampon)>=4:
            indirect=tampon[3].split(" ")
            if debug: print "indirect : ",indirect
            if indirect!=['']: phrase[syntagmes['Phrase'].index('IND')]=faire_gp(indirect)
        if len(tampon)>=5:
            ajout=tampon[4].split(" ")
            phrase[syntagmes['Phrase'].index('AJOUT')]=faire_gp(ajout)
        glose="\\"+recoder(verbeLemme,deaccent)+morphosyntax["V"]["FormesBase"][verbeFormeIndex].capitalize()+abs_genre.capitalize()+abs_nombre.capitalize()
        phrase[syntagmes['Phrase'].index('V')]=glose
        texte.append(glose)
        if print_glose:
            ajouterExemple(comment+"\\ex\\glll")
        else:
            ajouterExemple(comment+"\\ex\\gll")
        print comment,
        for mot in phrase:
            if mot!=0:
                printflat(mot,"{}")
        ajouterExemple(" ".join(accumulateur)+"\\\\")
        print comment,
        for mot in phrase:
            if mot!=0:
                printflat(mot,"P{}")
        ajouterExemple(" ".join(accumulateur)+"\\\\")
        if print_glose:
            print comment,
            for mot in phrase:
                if mot!=0:
                    printflat(mot,"G{}")
            ajouterExemple(" ".join(accumulateur)+"\\\\")
        traduction=(line.strip().rstrip('.')).split()
        start=1
#        accumulerMots(comment)
        for element in traduction:			# convertir les S majuscules à la finale des mots en minuscules
            if element!="":
                if start:
                    start=0
                    element=element.capitalize()
                caracteres=list(element)
                if caracteres[len(caracteres)-1]=='S':
                    caracteres[len(caracteres)-1]='s'
                accumulerMots("".join(caracteres).encode('utf8'))
        ajouterExemple(taches()+" ".join(accumulateur))
        del accumulateur[:]
        if print_coffee and random.randint(1,6)==1:
            stain=random.choice(["A","B","C","D"])
            alpha=random.random()/1.5
            angle=random.randint(0,360)
            xoff=random.randint(-200,0)
            ajouterExemple('\\\\\\cofe%sm{%.3f}{1}{%d}{%d}{0}' % (stain,alpha,angle,xoff))
ajouterExemple(comment+"\\end{exe}")
    
phrase_file.close()


# #################################################
# if ('options' in globals() and options.print_cloze) or print_racines:
#     tableau_racines_n=[]
#     tableau_racines_v=[]
#     print
#     print
#     print
#     print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%RACINES%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
#     print
#     print
#     print
#     print "%										NOMS"
#     print
#     for element in sorted(radical_n.keys()):
#         tableau_racines_n.append("%s & %s & \\textipa{%s} & \\textipa{%s} \\\\" % (element, radical_n[element][2], radical_n[element][0], radical_n[element][1]))
#     print_tableaux(2,tableau_racines_n,"",0,(head_n,tail,"%"))	
#     print
#     print
#     print
#     print "%										VERBES"	
#     print
#     for element in sorted(radical_v.keys()):
#         tableau_racines_v.append("%s & %s & \\textipa{%s} \\\\" % (element, radical_v[element][1], radical_v[element][0]))
#     print_tableaux(2,tableau_racines_v,"",0,(head_v,tail,"%"))	

# In[2560]:

if ('options' in globals() and options.print_cloze) or print_lexique:
    tab=(head,tail,"")
else:
    tab=(head,tail,"%")
ajouterVocabulaire(tab[2]+"\\begin{itemize}")
ajouterVocabulaire(tab[2]+"\\item NOMS\\\\[-3ex]")
print_tableaux(2,tableaux["N"],texte,8,tab)
ajouterVocabulaire(tab[2]+"\\item ADJECTIFS\\\\[-3ex]")
print_tableaux(3,tableaux["ADJ"],texte,11,tab)
ajouterVocabulaire(tab[2]+"\\item VERBES\\\\[-3ex]")
print_tableaux(2,tableaux["V"],texte,35,tab)
ajouterVocabulaire(tab[2]+"\\item DÉTERMINANTS\\\\[-3ex]")
print_tableaux(3,tableaux["DET"],texte,12,tab)
ajouterVocabulaire(tab[2]+"\\item PRÉPOSITIONS\\\\[-3ex]")
print_tableaux(3,tableaux["PREP"],texte,0,tab)
ajouterVocabulaire(tab[2]+"\\end{itemize}")


# if ('options' in globals() and options.print_cloze) or print_cloze:
#     print
#     print
#     print
#     print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%CLOZE%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
#     print
#     print
#     print
#     print "%										NOMS"	
#     for element in cloze_noms:
#         print "% ", element[0].translate(toipa)+";"+element[1]
#     print
#     print
#     print
#     print "%										VERBES"	
#     for element in cloze_verbes:
#         print "% ", element[0].translate(toipa)+";"+element[1]		

# In[2561]:

with open(serie+"Exemples.tex", 'wb') as output:
    for exemple in exemples:
        output.write(exemple+"\n")


# In[2562]:

with open(serie+"Vocabulaire.tex", 'wb') as output:
    for vocable in vocabulaire:
        output.write(vocable+"\n")


# In[2562]:



