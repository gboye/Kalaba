
# coding: utf-8

# In[32]:



#########################IMPORTS############################################
import codecs, optparse
import re, random
import sys,os,time
import string
import yaml
import ParFuMor as PFM
from ParFuMor import *
import pickle


# In[33]:

#########################VARIABLES##########################################
version=os.path.basename("__file__")
time_stamp='%s' % time.strftime("%y%m%d-%H%M")
debug=0
debug_now=0
print_no=False
print_coffee=False
print_commands=True
print_phrases=True
print_glose=1
print_lexique=False
print_cloze=False
print_racines=False
no_form="***"
genre=[u'M',u'F',u'A', u'I']
classe=[u'H',u'NH']
nombre=[u'SG',u'DU',u'PL',u'NSG']
nombre_sdp=[u'SG',u'DU',u'PL']
nombre_sp=[u'SG',u'NSG']
cas=[u'',u'ERG',u'ABS']
# no_grapho=['dormir', 'lit']
# no_phono=['gros', 'coussin']
no_grapho=['petit','Nabil',"sur"]
no_phono=["grand","autruche",'dans']
phono_no=u"XXXXX"
grapho_no=u"XXXXX"


# In[34]:

with open("Kalaba-Gloses.yaml", 'r') as stream:
    gloses=yaml.load(stream)
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


# In[35]:

lexemes=[]
graphies={}
lexique={}
base={}
categorie_v={}
temps_v={}
radical_n={}
radical_v={}
noms=[]
cloze_noms=[]
tableau_noms=[]
verbes=[]
cloze_verbes=[]
tableau_verbes=[]
determinants=[]
tableau_determinants=[]
prepositions=[]
tableau_prepositions=[]
adjectifs=[]
tableau_adjectifs=[]
francais=[]
kalaba=[]


# ####Définition des entêtes

# In[36]:

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


# In[37]:

tail = [
"\\hline"
"\\end{tabular}\\\\"
]


# ####Définition des segments

# In[38]:

consonnes=phonology["consonnes"]
voyelles=phonology["voyelles"]
gabarits=phonology["gabarits"]
derives=phonology["derives"]
nom_classe=phonology["nom_classe"]
nom_apo=phonology["apophonies"]

nom_mut=phonology["mutations"]


# ####Définition des catégories

# In[39]:

genres=gloses["N"]["Genre"]
types=gloses["V"]["Type"]
#verbe_classe=morphosyntax["V"]["Type"]
#verbe_genre=morphosyntax["V"]["Genre-Abs"]
#verbe_nombre=morphosyntax["V"]["Nombre-Abs"]
#verbe_temps=morphosyntax["V"]["Temps"]
i=2
verbe_forme={}
for forme in morphosyntax["V"]["FormesBase"]:
    verbe_forme[i]=forme
    i+=1
#det_nb=morphosyntax["DET"]["Nombre"]
#det_cas=morphosyntax["DET"]["Cas"]
#adjectif_genre=morphosyntax["ADJ"]["Genre"]
#adjectif_nb=morphosyntax["ADJ"]["Nombre"]
#adj_types_nombre=morphosyntax["ADJ"]["CF"]["Nombre"]
#adj_types_genre=morphosyntax["ADJ"]["CF"]["Genre"]


# In[40]:

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


# In[41]:

syntagmes=morphosyntax["Syntagmes"]


# In[42]:

contractions=morphosyntax["Contractions"]


# In[43]:

syllabes=phonology["syllabes"]


# In[44]:

def taches(chaine):
    result=[]
    choix=random.sample(["a","b","c","d","e","f","g","h"],len(chaine)//2+len(chaine)%2)
    for n in range(0, len(chaine), 2):
        result.append("\\cache%s{%s}" % (choix[n//2],chaine[n:n+2]))
    return "".join(result)


# In[45]:

def faire_tableau(tableau,tab=(head,tail,"")):
    if len(tableau)==0: return
    comment=tab[2]
    for element in tab[0]:
        print comment+element
    for element in tableau:
        print comment+element
    for element in tab[1]:
        print comment+element


# In[46]:

def print_tableaux(cols,tableau,texte="",debut=0,tab=(head,tail,"")):
    print tab[2]+"\\begin{multicols}{"+str(cols)+"}"
    if texte!="":
        table=filtrer_tableau(tableau,texte)
    else:
        table=tableau
    chunk=(len(table)-debut*cols)/cols+1
    faire_tableaux(table,debut,cols,tab)
    print tab[2]+"\\end{multicols}"
    


# In[47]:

#def faire_tableaux(tableau,taille=16,debut=16,nombre=0):
#	for i in range(nombre):
#		faire_tableau(tableau[debut*i:debut*(i+1)])
#	longueur=len(tableau)-nombre*debut
#	chunks=longueur/taille
##	print longueur, taille, chunks
#	for i in range(chunks+1):
##		print i
#		faire_tableau(tableau[nombre*debut+taille*i:nombre*debut+taille*(i+1)])

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
#	print longueur, taille, chunks
    for i in range(nombre):
#		print i
        faire_tableau(table[chunks*i:chunks*(i+1)],tab)
    if reste:
        faire_tableaux(reste,0,nombre,tab)


# In[48]:

def filtrer_tableau(tableau,filtre):
    result=[]
    for line in tableau:
        elements=line.split(" ")
        if elements[0] in filtre: result.append(line)
    return result


# In[49]:

def faire_gn(depart,cas):
#    print "faire_gn",[depart,cas]
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
    for umot in groupe_nom:
#        print "umot", [umot]
#        mot=umot.encode("utf8")
        mot=umot
        if reste==0:
            if mot=="deux":
                nombre="DU"
                if det==[]: det.append(PFM.lexique.formeLexeme["des"][0])
            else:
                if debug: 
                    print [mot],
                    print PFM.lexique.formeLexeme[mot][0]
                nomLexeme=PFM.lexique.formeLexeme[mot][0]
                categorie=PFM.lexique.lexemes[nomLexeme].classe
                if categorie in PFM.hierarchieCF.classes["N"]:
                    tete=categorie
                    if debug: print "tête :", tete
                    tampon=tete.split('.')
                    classe=tampon[0]
                    try:
                        type=tampon[1]
                    except IndexError:
                        type=''
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


# In[50]:

def faire_gp(groupe_prep):
    mots=[]
    groupe_prep=etendre_contraction(groupe_prep)
    if debug: print "faire_gp", groupe_prep
    if groupe_prep[0]!="à" :
        if debug: print "PREP!=à"
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


# In[51]:

def etendre_contraction(liste):
    result=[]
    if liste[0] in contractions.keys():
        if debug: print "EXT : ", liste, contractions[liste[0]],liste[1:] 
        result.extend(contractions[liste[0]])
        result.extend(liste[1:])
    else:
        result=liste
    #for element in liste:
    #	if element in contractions.keys(): result.extend(contractions[element])
    #	else: result.append(element)
    return result


# In[52]:

def printflat(liste,suffixe="",prefixe=""):
    if debug: print "printflat", liste
    if not isinstance(liste, basestring):
        for element in liste:
            print prefixe,
            printflat(element,suffixe)
    else: print prefixe,liste+suffixe,


# In[53]:

#######################
#
#	INITIALISATION DES VARIABLES
#
#######################

#genres=nom_classe.keys()
#types=verbe_classe.keys()
#nombres=nom_nombre.keys()
#cases=nom_cas.keys()
#temps=verbe_temps.keys()

try:
    __IPYTHON__ 
    ipython=True
except: 
    ipython=False


# In[54]:

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


# ####Ouverture du fichier lexique

# ####Ouverture du fichier phrases

# In[55]:

try:
    phrase_file = codecs.open(phrase_nom,"r","utf-8")
except IOError:
    print 'I could not open the sentence file', phrase_nom
    sys.exit()


# In[56]:

def recoder(chaine,table):
    if type(chaine)==str:
        temp=unicode(chaine.decode('utf8')).translate(table)
        result=temp.encode('utf8')
    elif type(chaine)==unicode:
        result=chaine.translate(table)
    return result


# In[57]:

accentedIn = unicode(phonology["translations"]["deaccent"]["in"])
deaccentIn = [ord(char) for char in accentedIn]
deaccentOut = unicode(phonology["translations"]["deaccent"]["out"])
deaccent = dict(zip(deaccentIn, deaccentOut))


# In[58]:

tipaIn = unicode(phonology["translations"]["ipa"]["in"])
ipaIn = [ord(char) for char in tipaIn]
ipaOut = unicode(phonology["translations"]["ipa"]["out"])
toipa = dict(zip(ipaIn, ipaOut))


# In[59]:

lexemes=[]
graphies={}
noms=[]
tableau_noms=[]
verbes=[]
tableau_verbes=[]
determinants=[]
tableau_determinants=[]
prepositions=[]
tableau_prepositions=[]
adjectifs=[]
tableau_adjectifs=[]
francais=[]
kalaba=[]


# In[60]:

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
graphies={}
abs_genre=""
abs_nombre=""


# In[61]:

forme="achetaient"
verbeLexeme=PFM.lexique.formeLexeme[forme][0]
formeIndex=PFM.lexique.lexemes[verbeLexeme].formes.index(forme)
morphosyntax["V"]["FormesBase"][formeIndex].capitalize()


# In[62]:

if print_phrases:
    comment=""
else:
    comment="%"
print comment+"\\begin{exe}"
for line in phrase_file:
    phrase=[0 for i in range(len(syntagmes['Phrase']))]
    #
    # Insertion du replace("'"," ") pour la gestion des articles élidés en français
    #
#    tampon=(line.strip().rstrip('.')).replace("'"," ").split("\t")
    tampon=(line.strip().rstrip('.')).replace("'"," ").encode("utf8").split("\t")
    if not tampon[0].startswith("#"):
        verbe=tampon[1].split(" ")
#        verbeForme=verbe[0].encode("utf8")
        verbeForme=verbe[0]
        if len(PFM.lexique.formeLexeme[verbeForme])!=1:
            print "FORME AMBIGUË"
        verbeLexeme=PFM.lexique.formeLexeme[verbeForme][0]
        (formeCitation,typeVerbe)=verbeLexeme.split(".")
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
# 		verbe=tampon[1].split(" ")
# 		if debug: print "verbe :", verbe
        if len(tampon)>=3:
            objet=tampon[2].split(" ")
            if debug: print "objet : ",objet
            if objet!=['']: phrase[syntagmes['Phrase'].index('OBJ')]=faire_gn(objet,obj_cas)
        if len(tampon)>=4:
            indirect=tampon[3].split(" ")
            if debug: print "indirect : ",indirect
            if indirect!=['']: phrase[syntagmes['Phrase'].index('IND')]=faire_gp(indirect)
        #if len(tampon)>=4:
        #	indirect=tampon[3].split(" ")
        #	if indirect!=['']: phrase[2]=faire_gp(indirect)
        if len(tampon)>=5:
            ajout=tampon[4].split(" ")
            phrase[syntagmes['Phrase'].index('AJOUT')]=faire_gp(ajout)
#		glose=faire_glose(base[verbe[0]],suj_genre,suj_num)
#		if debug: print verbe[0],categorie_v[verbe[0]], temps_v[verbe[0]], suj_genre, suj_nombre
#		glose="\\"+base[verbe[0]]+categorie_v[verbe[0]].capitalize()+temps_v[verbe[0]].capitalize()+suj_genre.capitalize()+suj_nombre.capitalize()
#  		if categorie_v[verbe[0]] == "VI":
#  			glose="\\"+base[verbe[0]]+categorie_v[verbe[0]].capitalize()+temps_v[verbe[0]].capitalize()+suj_genre.capitalize()+suj_nombre.capitalize()
#  		else:
        glose="\\"+recoder(verbeLemme,deaccent)+morphosyntax["V"]["FormesBase"][verbeFormeIndex].capitalize()+abs_genre.capitalize()+abs_nombre.capitalize()
        phrase[syntagmes['Phrase'].index('V')]=glose
        texte.append(glose)
        if print_glose:
            print comment+"\\ex\\glll"
        else:
            print comment+"\\ex\\gll"
        print comment,
        for mot in phrase:
            if mot!=0:
                printflat(mot,"{}")
        print "\\\\"
        print comment,
        for mot in phrase:
            if mot!=0:
                printflat(mot,"P{}")
        print "\\\\"
        if print_glose:
            print comment,
            for mot in phrase:
                if mot!=0:
                    printflat(mot,"G{}")
            print "\\\\"
        traduction=(line.strip().rstrip('.')).split()
        start=1
#        sys.stdout.write(comment)
        print comment,
        for element in traduction:			# convertir les S majuscules à la finale des mots en minuscules
            if element!="":
                if start:
                    start=0
                    element=element.capitalize()
#                else:
#                    sys.stdout.write(' ')
#                print 
                caracteres=list(element)
                if caracteres[len(caracteres)-1]=='S':
                    caracteres[len(caracteres)-1]='s'
#                sys.stdout.write("".join(caracteres).encode('utf8'))
                print "".join(caracteres).encode('utf8'),
#        sys.stdout.write('.\r')
        print
        if print_coffee and random.randint(1,6)==1:
            stain=random.choice(["A","B"])
            alpha=random.random()/1.5
            angle=random.randint(0,360)
            xoff=random.randint(-200,0)
#            sys.stdout.write('\\\\\\cofe%sm{%.3f}{1}{%d}{%d}{0}' % (stain,alpha,angle,xoff))
            print '\\\\\\cofe%sm{%.3f}{1}{%d}{%d}{0}' % (stain,alpha,angle,xoff)
print comment+"\\end{exe}"
    
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

# if ('options' in globals() and options.print_cloze) or print_lexique:
#     tab=(head,tail,"")
# else:
#     tab=(head,tail,"%")
# print tab[2]+"\\begin{itemize}"
# print tab[2]+"\\item NOMS\\\\[-3ex]"
# print_tableaux(2,tableaux["N"],texte,21,tab)
# print tab[2]+"\\item ADJECTIFS\\\\[-3ex]"
# print_tableaux(3,tableaux["ADJ"],texte,4,tab)
# print tab[2]+"\\item VERBES\\\\[-3ex]"
# print_tableaux(2,tableaux["V"],texte,35,tab)
# print tab[2]+"\\item DETERMINANTS\\\\[-3ex]"
# print_tableaux(3,tableaux["DET"],texte,12,tab)
# print tab[2]+"\\item PREPOSITIONS\\\\[-3ex]"
# print_tableaux(3,tableaux["PREP"],texte,0,tab)
# print tab[2]+"\\end{itemize}"

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
