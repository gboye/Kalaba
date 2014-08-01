# encoding: utf-8

#########################IMPORTS############################################
import re
import codecs
import sys
import string
import random

#########################VARIABLES##########################################
debug=0
debug_now=1
ordre="GP"
print_glose=1
print_lexique=1
no_form="***"
genre=['M','F','A', 'I']
classe=['H','NH']
nombre=['SG','DU','PL','NSG']
nombre_sdp=['SG','DU','PL']
nombre_sp=['SG','NSG']
cas=['','ERG','ABS']
# no_grapho=['dormir', 'lit']
# no_phono=['gros', 'coussin']
no_grapho=[]
no_phono=[]
phono_no="XXXXX"
grapho_no="XXXXX"

lexemes=[]
graphies={}
lexique={}
base={}
categorie_v={}
temps_v={}
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

#########################CONSTANTS##########################################
consonnes="ptkbdgmnNfsSvzZrljw"
voyelles="iueoa"
stops={'p':'p', 't':'t', 'k':'k', 'b':'b', 'd':'d', 'g':'g'}
nasals={'m':'m', 'n':'n', 'N':'ŋ'}
fricatives={'f':'f', 's':'s', 'S':'ʃ', 'v':'v', 'z':'z', 'Z':'ʒ'}
liquids={'r':'r', 'l':'l'}
glides={'w':'w', 'j':'j'}
vowels={'i':'i', 'u':'u', 'e':'e', 'o':'o', 'a':'a'}
phonemes=stops.copy()
phonemes.update(fricatives)
phonemes.update(nasals)
phonemes.update(liquids)
phonemes.update(glides)
phonemes.update(vowels)
neutralisations={'à':'a', 'â':'a', 'ç':'c', 'é':'e', 'è':'e', 'ê':'e', 'î':'i', 'ù':'u', 'ô':'o'}


gabarits=['DU','PL','PRS','PST']
derives={'A':'V','D':'C'}
nom_classe={'A':'', 'B':'i', 'C':'a', 'D':'u'}
nom_apo={'':'i', 'i':'a', 'a':'u', 'u':'u', 'e':'o', 'o':'o'}
nom_nombre={'SG':'','DU':'1A2V2C3','PL':'1U2A33D'}
nom_cas={'Ø':'','NOM':'ki','ACC':'la','DAT':'bu'}
verbe_classe={'VT':'a', 'VI':'e', 'VD':'o'}
verbe_genre={'A':'a', 'B':'i', 'C':'u', 'D':'e'}
verbe_nombre={'SG':'s','DU':'d','PL':'t'}
verbe_temps={'PRS':'1V22C3A', 'PST':'1C12A33D'}
verbe_forme={2:'INF',3:'PRS',4:'PRS',5:'PST',6:'PST'}
det_nb={'SG':'a', 'DU':'i', 'PL':'u'}
det_cas={'Ø':'n','NOM':'k','ACC':'d','DAT':'g'}
adjectif_genre={'A':'t', 'B':'b', 'C':'k', 'D':'n'}
adjectif_nb={'SG':'u', 'DU':'i', 'PL':'a'}

syntagmes={
	'Phrase':['AJOUT','V','COMP','SUJ','OBJ','IND'],
	'GN':['DET','GP', 'GADJ', 'N'],
	'GP':['PREP','GN'],
	'GADJ':['GP','ADV','ADJ'],
	}

contractions={
	'au':['à', 'le'],
	'aux':['à','les'],
	'du':['de','le'],
	'des':['de','les']
}

#######
#
# Insertion de \blanc{XXX} autour de la chaine dans le cas de LaTeX
#
#######
def gloss_phono(gloss,phono):
	if ordre =="GP":
		gloss_first=1
	elif ordre=="PG":
		gloss_first=0
	else:
		gloss_first=random.getrandbits(1)
	if gloss_first:
		result=gloss+";"+phono
	else:
		result=phono+";"+gloss
	return result

def neutralize(chaine):
	result=""
	for character in chaine:
#		char=character.encode('utf-8')
		char=character
		if char in neutralisations.keys():
			result=result+neutralisations[char]
		else:
			result=result+char
	return result

def phonemize(chaine):
	result=""
	for character in chaine:
		char=character.encode('utf-8')
		result=result+phonemes[char]
	return result


def blanc(chaine):
	result=chaine
	return result

def apophone(voyelle):
	result=nom_apo[voyelle]
	return result

def fait_racine(simple):
	if debug: print "simple : ", simple
	c=1
	result={'1':'','2':'','3':'','V':''}
	for lettre in simple:
		if debug: print "lettre : ",lettre
		if lettre in consonnes:
			result[str(c)]=lettre
			c=c+1
		elif lettre in voyelles:
			if result['V']=='':
				result['V']=lettre
		else:
			if debug: print "erreur sur racine", simple
	return result

def affixe(debut, fin):
	return debut+fin

def gabarit(forme,racine):					#met la racine dans le gabarit forme
	if debug: print "gabarit : ", forme, racine
	result=""
	for signe in forme:
		if signe in "123":				#place les consonnes en 1, 2, 3
			result=result+racine[signe]
		elif signe in "VC":				#place la voyelle radicale V et la voyelle de classe C
			result=result+racine[signe]
		elif signe in "AD":
			result=result+apophone(racine[derives[signe]])	#place les apophones de V et C (resp. A et D)
		elif signe in "U":
			result=result+apophone(apophone(racine['V']))	#place le bi-apophone de V
		else:
			result=result+signe
		if debug: print signe, result
	if debug: print result
	return result

def n_nombre(nombre, nom, classe):
	radical=nom
	if debug: print "radical : ",radical
	racine=fait_racine(radical)
	racine["C"]=nom_classe[classe]
	if debug: print "racine : ", radical, racine
	forme=nom_nombre[nombre]
	if debug: print "n_nombre :", nombre, forme
	if nombre in gabarits :
		if debug: print "forme gabaritique : ", forme, racine
		result=gabarit(forme, racine)
	else:
		result=affixe(nom_nombre[nombre], radical)
	return result
	
def n_cas(cas, nom, classe):
	if cas!='Ø':
		result=nom_cas[cas]+nom
	else:
		result=nom
	return result

def paradigme_nom(nom):
	genre=nom[0]
	racine=nom[1]
	lemme=nom[2].lower()
	if debug: print lemme, racine, genre
	for nombre in nombres:
		if debug: print nombre
		if debug: print nombre, racine, genre
		phono_n=n_nombre(nombre, racine, genre)
		if nombre in gabarits:
			gloss_n=lemme+str(blanc("."+genre.capitalize()+"x"+nombre.upper()))
		else:
			gloss_n=lemme+str(blanc("."+genre.capitalize()+"."+nombre.upper()))
		for case in cases:
			if debug: print case
			phono=n_cas(case, phono_n, classe)
			grapho=phono
			if case!='Ø':
				gloss=str(blanc(case.upper()+"-"))+gloss_n
				ref=neutralize(lemme)+genre.capitalize()+nombre.capitalize()+case.capitalize()
			else:
				gloss=gloss_n
				ref=neutralize(lemme)+genre.capitalize()+nombre.capitalize()
			if nom[2] in no_grapho:
				noms.append("\\newcommand{\\"+ref+"}{\\strutgb{0pt}"+grapho_no+"}")
				grapho=grapho_no
			else:
				noms.append("\\newcommand{\\"+ref+"}{\\strutgb{0pt}\\grapho{"+grapho+"}}")
			if nom[2] in no_phono:
				noms.append("\\newcommand{\\"+ref+"P}{"+phono_no+"}")
				phono=phono_no
			else:
				noms.append("\\newcommand{\\"+ref+"P}{\\textipa{"+phono+"}}")
			graphies["\\"+ref]=grapho
			noms.append("\\newcommand{\\"+ref+"G}{"+gloss+"}")
			tableau_noms.append(gloss_phono(gloss,phonemize(phono)))

def v_temps(tense, verbe, type, genre):
	radical=verbe
	if debug: print "radical : ",radical
	racine=fait_racine(radical)
	racine["V"]=verbe_classe[type]
	racine["C"]=verbe_genre[genre]
	if debug: print "racine : ", radical,type,genre, racine
	forme=verbe_temps[tense]
	if debug: print "v_temps :", tense, forme
	if tense in gabarits :
		if debug: print "forme gabaritique : ", forme, racine
		result=gabarit(forme, racine)
	else:
		result=affixe(verbe_temps[tense], radical)
	return result
	
def v_nombre(nombre, verbe):
	if debug: print nombre, verbe
	result=verbe_nombre[nombre]+verbe
	return result

def paradigme_verbe(verbe):
	type=verbe[0]
	racine=verbe[1]
	lemme=verbe[2]
	if debug: print lemme, racine, type
	for tense in temps:
		if debug: print tense
		for genre in genres:
			if debug: print genre
			phono_t=v_temps(tense,racine,type,genre)
			if tense in gabarits:
				gloss_t=lemme.lower()+str(blanc("."+type.upper()+"x"+tense.upper()+"x"+genre.upper()))
			else:
				gloss_t=lemme.lower()+str(blanc("."+type.upper()+"-"+tense.upper()+"-"+genre.upper()))
			for nombre in nombres:
				if debug: print nombre
				phono=v_nombre(nombre,phono_t)
				grapho=phono
				gloss=str(blanc(nombre+"-"))+gloss_t
				ref=neutralize(lemme)+type.capitalize()+tense.capitalize()+genre.capitalize()+nombre.capitalize()
				if verbe[2] in no_grapho:
					verbes.append("\\newcommand{\\"+ref+"}{\\strutgb{0pt}"+grapho_no+"}")
					grapho=grapho_no
				else:
					verbes.append("\\newcommand{\\"+ref+"}{\\strutgb{0pt}\\grapho{"+grapho+"}}")
				if verbe[2] in no_phono:
					verbes.append("\\newcommand{\\"+ref+"P}{"+phono_no+"}")
					phono=phono_no
				else:
					verbes.append("\\newcommand{\\"+ref+"P}{\\textipa{"+phono+"}}")
				graphies["\\"+ref]=grapho
				
				verbes.append("\\newcommand{\\"+ref+"G}{"+gloss+"}")
				tableau_verbes.append(gloss_phono(gloss,phonemize(phono)))

def adj_nombre(nombre, adjectif):
	if debug: print nombre, adjectif
	result=adjectif+adjectif_nb[nombre]
	return result

def adj_genre(genre, adjectif):
	if debug: print genre, adjectif
	result=adjectif+adjectif_genre[genre]
	return result

def paradigme_adj(lexeme):
	radical=lexeme[1]
	lemme=lexeme[2]
	if debug: print lemme, radical
	for nombre in nombres:
		if debug: print genre
		phono_n=adj_nombre(nombre,radical)
		for genre in genres:
			phono=adj_genre(genre,phono_n)
			gloss=lemme.lower()+str(blanc("-"+nombre.upper()+"-"+genre.upper()))
			ref=lemme.lower()+nombre.capitalize()+genre.capitalize()
			grapho=phono
			if lexeme[2] in no_grapho:
				adjectifs.append("\\newcommand{\\"+ref+"}{\\strutgb{0pt}"+grapho_no+"}")
				grapho=grapho_no
			else:
				adjectifs.append("\\newcommand{\\"+ref+"}{\\strutgb{0pt}\\grapho{"+grapho+"}}")
			if lexeme[2] in no_phono:
				adjectifs.append("\\newcommand{\\"+ref+"P}{"+phono+"}")
				phono=phono_no
			else:
				adjectifs.append("\\newcommand{\\"+ref+"P}{\\textipa{"+phono+"}}")
			graphies["\\"+ref]=grapho
			adjectifs.append("\\newcommand{\\"+ref+"G}{"+gloss+"}")
			tableau_adjectifs.append(gloss_phono(gloss,phonemize(phono)))
			
			

def paradigme_det(lexeme):
	radical=lexeme[1]
	lemme=lexeme[2]
	if debug: print lemme, radical
	for nombre in nombres:
		if debug: print nombre
		phono_n=radical+det_nb[nombre]
		for case in cases:
			if case!='Ø':
				phono=phono_n+det_cas[case]
				gloss=lemme.upper()+str(blanc("-"+nombre.upper()+"-"+case.upper()))
				ref=lemme.lower()+nombre.capitalize()+case.capitalize()
			else:
				phono=phono_n
				gloss=lemme.upper()+str(blanc("-"+nombre.upper()))
				ref=lemme.lower()+nombre.capitalize()
			grapho=phono
			if lexeme[2] in no_grapho: grapho=grapho_no
			if lexeme[2] in no_phono: phono=phono_no
			determinants.append("\\newcommand{\\"+ref+"}{\\strutgb{0pt}\\grapho{"+grapho+"}}")
			graphies["\\"+ref]=grapho
			determinants.append("\\newcommand{\\"+ref+"P}{\\textipa{"+phono+"}}")
			determinants.append("\\newcommand{\\"+ref+"G}{"+gloss+"}")
			if print_glose:
				tableau_determinants.append("\\"+ref+" & \\"+ref+"P & \\"+ref+"G \\\\")
			else:
				tableau_determinants.append("\\"+ref+" & \\"+ref+"P & \\\\")

def paradigme_prep(lexeme):
	phono=lexeme[1]
	lemme=neutralize(lexeme[2])
	gloss=lemme.upper()
	grapho=phono
	ref=lemme.upper()
	if lexeme[2] in no_grapho: grapho=grapho_no
	if lexeme[2] in no_phono: phono=phono_no
	prepositions.append("\\newcommand{\\"+ref+"}{\\strutgb{0pt}\\grapho{"+grapho+"}}")
	graphies["\\"+ref]=grapho
	prepositions.append("\\newcommand{\\"+ref+"P}{\\textipa{"+phono+"}}")
	prepositions.append("\\newcommand{\\"+ref+"G}{"+gloss+"}")
	if print_glose:
		tableau_prepositions.append("\\"+ref+" & \\"+ref+"P & \\"+ref+"G \\\\")
	else:
		tableau_prepositions.append("\\"+ref+" & \\"+ref+"P & \\\\")


def faire_tableau(tableau):
	if len(tableau)==0: return
	print "\\begin{tabular}[t]{|c|l|l|}"
	print "\\addlinespace[-1.0em]\\hline"
	print "	Mot & Roman & Glose  \\\\"
	print "\\hline\\strutgh{14pt}%"
	for element in tableau:
		print element
	print "\\hline"
	print "\\end{tabular}\\\\"
#	print "\\smallskip"
#	print

def print_tableaux(cols,tableau,texte,debut=0):
	print "\\begin{multicols}{"+str(cols)+"}"
	table=filtrer_tableau(tableau,texte)
	chunk=(len(table)-debut*cols)/cols+1
	faire_tableaux(table,debut,cols)
	print "\\end{multicols}"
	
def print_table(tableau):
	for element in tableau:
		print "#EX;"
		print element

#def faire_tableaux(tableau,taille=16,debut=16,nombre=0):
#	for i in range(nombre):
#		faire_tableau(tableau[debut*i:debut*(i+1)])
#	longueur=len(tableau)-nombre*debut
#	chunks=longueur/taille
##	print longueur, taille, chunks
#	for i in range(chunks+1):
##		print i
#		faire_tableau(tableau[nombre*debut+taille*i:nombre*debut+taille*(i+1)])

def faire_tableaux(tableau,debut=16,nombre=1):
	reste=[]
	if debug: print nombre,debut,tableau
	if debut!=0:
		for i in range(nombre):
			faire_tableau(tableau[debut*i:debut*(i+1)])
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
		faire_tableau(table[chunks*i:chunks*(i+1)])
	if reste:
		faire_tableaux(reste,0,nombre)

def filtrer_tableau(tableau,filtre):
	result=[]
	for line in tableau:
		elements=line.split(" ")
		if elements[0] in filtre: result.append(line)
	return result


def printflat(liste,suffixe=""):
	if debug: print "printflat", liste
	if not isinstance(liste, basestring):
		for element in liste:
			printflat(element,suffixe)
	else: print liste+suffixe,


#######################
#
#	INITIALISATION DES VARIABLES
#
#######################

genres=nom_classe.keys()
types=verbe_classe.keys()
nombres=nom_nombre.keys()
cases=nom_cas.keys()
temps=verbe_temps.keys()


################
#
# LECTURE DU FICHIER DE LEXEMES
#
#		LES LIGNES QUI COMMENCENT PAR # SONT IGNOREES
#
################
try:
    lexeme_file = codecs.open(sys.argv[1],"r","utf-8")
except IOError:
    print 'I could not open the lexeme file', sys.argv[1]
    sys.exit()

# translit=string.maketrans('iueoaftgzZvjkSpN','tgazpHTGZJVkXyxI')
# deaccent=string.maketrans('àâçéèêîùô','aaceeeiuo')

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

for line in lexeme_file:
	tampon=(line.strip()).encode('utf-8').split(',')
	if not tampon[0].startswith("#"):
		lexemes.append(tampon)
lexeme_file.close()


for lexeme in lexemes:
	lemme=neutralize(lexeme[2])
	categorie=lexeme[0]
	lexique[lemme]=categorie
	for forme in lexeme[2:]:
		base[forme]=lemme
		if debug: print "base :", forme, lexeme[2]
		if categorie in types:
			categorie_v[forme]=categorie
			temps_v[forme]=verbe_forme[lexeme.index(forme)]
			if debug: print forme, lemme, lexeme.index(forme), temps_v[forme]
	if lexeme[0] in genres:
		paradigme_nom(lexeme)
	elif lexeme[0] in types:
		paradigme_verbe(lexeme)
	elif lexeme[0]=="ADJ":
		paradigme_adj(lexeme)
	elif lexeme[0] in ["DEF","IND","DEM"]:
		paradigme_det(lexeme)
	elif lexeme[0]=="PREP":
		paradigme_prep(lexeme)
	else: print "erreur de catégorie : ",lexeme[0]
	
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
#################################################
if print_lexique:
#	print "Noms"
	print_table(tableau_noms)
#	print "Adjectifs"
#	print_table(tableau_adjectifs)
#	print "Verbes"
#	print_table(tableau_verbes)

