# coding: utf-8
#import itertools
import re

gloses={}

def depthDict(element):
    max=0
    if type(element)==type({}):
        for k in element:
            depth=depthDict(element[k])
            if depth>max:
                max=depth
        return max+1
    else:
        return 0

def modifierForme(forme,transformation):
    m=re.match("^([^+]*)\+([^+]*)$",transformation)
    if m:
        if m.group(1)=="X":
            suffixe=m.group(2)
            prefixe=""
        elif m.group(2)=="X":
            prefixe=m.group(1)
            suffixe=""
    else:
        m=re.match("^([^+]*)\+([^+]*)\+([^+]*)$",transformation)
        if m:
            if m.group(2)=="X":
                prefixe=m.group(1)
                suffixe=m.group(3)
    if prefixe!="" and suffixe!="":
        affixe="circonfixe"
    elif prefixe!="":
        affixe="préfixe"
    elif suffixe!="":
        affixe="suffixe"
    else:
        affixe=""
    return (prefixe+forme+suffixe,affixe)

def modifierGlose(glose,sigma,affixe):
    '''
    à remplir
    '''
    mods=[]
    attributValeurs=sigma.split(",")
    for attributValeur in attributValeurs:
        (attribut,valeur)=attributValeur.split("=")
        mods.append(valeur)
    mod=".".join(mods)
    if affixe=="suffixe":
        glose=glose+"-"+mod
    elif affixe=="préfixe":
        glose=mod+"-"+glose
    elif affixe=="circonfixe":
        glose=mod+"+"+glose+"+"+mod
    return glose
    
class Paradigmes:
    '''
    information sur les cases flexionnelles par catégorie
    '''
    def __init__(self):
        self.cases={}
        self.categories=[]
        
    def addForme(self,cat,proprietes):
        sigma=", ".join(proprietes)
        cle={sigma:proprietes}
        if not cat in self.categories:
            self.categories.append(cat)
        if not cat in self.cases:
            self.cases[cat]=[]
        if not cle in self.cases[cat]:
            self.cases[cat].append(cle)
    
    def getSigmas(self,classe):
        sigmas=[]
        if classe in hierarchieCF.categorie:
            cat=hierarchieCF.categorie[classe]
            filtre="%s=%s"%(hierarchieCF.getFeature(cat,classe),classe)
        else:
            cat=classe
            filtre=""
        if cat in self.cases:
            for element in self.cases[cat]:
                for cle in element:
                    if filtre in cle:
                        sigmas.append(cle)
            return sigmas
        else:
            return [cat]

paradigmes=Paradigmes()

class HierarchieCF:
    '''
    hiérarchie des classes flexionnelles
    '''
    def __init__(self):
        self.classes={}
        self.superieur={}
        self.categorie={}
        self.trait={}
        
    def addCategory(self,category,classe):
        if not category in self.classes:
            self.classes[category]=[]
        self.classes[category].append(classe)
        self.superieur[classe]=category
        if category in gloses:
            self.categorie[classe]=category
        else:
            self.categorie[classe]=self.categorie[category]
            category=self.categorie[category]
        for attribut in gloses[category]:
            if set(gloses[category][attribut])==set(hierarchieCF.classes[category]):
                for valeur in gloses[category][attribut]:
                    hierarchieCF.addFeature(category,valeur,attribut)
                    
    def addFeature(self,category,classe,feature):
        self.trait[category+"-"+classe]=feature
        
    def getFeature(self,category,classe):
        cle=category+"-"+classe
        if cle in self.trait:
            return self.trait[category+"-"+classe]
        else:
            return "Catégorie"
        
    def categoryLookup(self,categorie):
        if categorie in gloses:
            return categorie
        else:
            return self.categoryLookup(self.categorie[categorie])
    	    	   
    def getCategory(self,classe):
        '''
        donne la catégorie correspondant à une classe ou à une catégorie
        '''
        if classe in self.categorie:
            return self.categorie[classe]
        elif classe in self.classes:
            return classe
        else:
            return classe

hierarchieCF=HierarchieCF()

class Forme:
    '''
    sigma et forme fléchie
    '''
    def __init__(self,sigma,forme,glose):
        self.sigma=sigma
        self.forme=forme
        self.glose=glose
        
    def __repr__(self):
        return "%s:\t%s %s"%(self.sigma,self.forme, self.glose)
    
class Tableau:
    '''
    liste de sigmas
    '''
    def __init__(self,classe,stem,nom):
        self.cases=[]
        self.stem=stem
        self.nom=nom
        categorie=hierarchieCF.getCategory(classe)
        for case in paradigmes.getSigmas(classe):
            forme=self.stem
            glose=self.nom 
            derivations=regles.getRules(categorie,case)
            if derivations:
                for derivation in derivations:
                    (forme,affixe)=modifierForme(forme,derivation[0])
                    glose=modifierGlose(glose,derivation[1],affixe)
            flexion=Forme(case,forme,glose)
            self.cases.append(flexion)
            
    def __repr__(self):
        listCases=[]
        for case in self.cases:
            listCases.append(str(case))
        return self.stem+" :\n"+"\n\t".join(listCases)

class Lexeme:
    '''
    Formes fléchies d'un lexème suivant sa classe flexionnelle
    '''
    def __init__(self,stem,classe,nom):
        self.stem=stem
        self.classe=classe
        self.nom=nom
        self.paradigme=Tableau(classe,stem,nom)
        self.formes=[]

    def __repr__(self):
        return "%s, %s, %s\n%s\n"%(self.stem,self.classe,self.nom,self.paradigme)
    
    def addForme(self,*formes):
        for forme in formes:
            self.formes.append(forme)
        
class Lexique:
    '''
    Lexique de Lexèmes
    '''
    def __init__(self):
        self.lexemes={}
    
    def addLexeme(self,classe,stem,*formes):
        if classe!=hierarchieCF.getCategory(classe):
            nom=formes[0]+"."+classe
        else:
            nom=formes[0]
        self.lexemes[nom]=Lexeme(stem,classe,nom)
        self.lexemes[nom].addForme(*formes)
    
    def getLexemes(self,nom):
        if nom in self.lexemes:
            return [self.lexemes[nom]]
        else:
            return [lexeme for (vedette, lexeme) in self.lexemes.iteritems() if nom in vedette]

lexique=Lexique()

class Regles:
    '''
    Blocs de règles par catégorie
    '''
    def __init__(self):
        self.blocs={}
        
    def addBlocs(self,category,blocs):
        if not category in self.blocs:
            self.blocs[category]=blocs
            
    def getRules(self,category,case):
        if category in self.blocs:
            rules=[]
            sortBlocs=sorted(self.blocs[category],key=int)
            for num in sortBlocs:
                sortSigmas=sorted(self.blocs[category][num],key=lambda x: len(x.split("=")),reverse=True)
                for sigma in sortSigmas:
                    traits=sigma.split(",")
                    sigmaCase=True
                    for trait in traits:
                        sigmaCase=sigmaCase and trait in case
                    if sigmaCase:
                        rules.append((self.blocs[category][num][sigma],sigma))
                        break
            return rules
        else:
            return []

regles=Regles()

def analyserStems(niveau):
    depthNiveau=depthDict(niveau)
    if depthNiveau>1:
        for element1 in niveau:
            depthElement=depthDict(niveau[element1])
            if depthElement>=2:
                for element2 in niveau[element1]:
                    hierarchieCF.addCategory(element1,element2)
                analyserStems(niveau[element1])
            else:
                for forme in niveau[element1]:
                    if isinstance(niveau[element1][forme],str):
                        lexique.addLexeme(element1,forme,niveau[element1][forme])
                    elif isinstance(niveau[element1][forme],unicode):
                        lexique.addLexeme(element1,forme,niveau[element1][forme].encode('utf8'))
                    elif isinstance(niveau[element1][forme],list):
                        lexique.addLexeme(element1,forme,*niveau[element1][forme])
                    else:
                        print "PB",element1,forme,niveau[element1][forme]
