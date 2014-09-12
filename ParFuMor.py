# coding: utf-8
import re

gloses={}
phonology={}
verbose=False

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

def blanc(chaine):
    return "\\blanc{"+chaine+"}"

def modifierForme(forme,transformation):
    def extraireRacine(simple):
        if verbose: print "simple : ", simple
        c=1
        result={'1':'','2':'','3':'','V':''}
        for lettre in simple:
            if verbose: print "lettre : ",lettre
            if lettre in phonology["consonnes"]:
                result[str(c)]=lettre
                c=c+1
            elif lettre in phonology["voyelles"]:
                if result['V']=='':
                    result['V']=lettre
            else:
                if verbose: print "erreur sur racine", simple
        return result
        
    def appliquerGabarit(forme,racine):					
        '''
        met la racine dans le gabarit forme
        '''
        if verbose: print "gabarit : ", forme, racine
        result=""
        for signe in forme:
            if signe in "123":				#place les consonnes en 1, 2, 3
                result=result+racine[signe]
            elif signe in "456":
                result=result+phonology["mutations"][racine[str(int(signe)-3)]]
            elif signe in "789":
                result=result+phonology["mutations"][phonology["mutations"][racine[str(int(signe)-6)]]]
            elif signe in "V":				#place la voyelle radicale V et la voyelle de classe C
                result=result+racine[signe]
            elif signe in "A":
                result=result+phonology["apophonies"][racine[phonology["derives"][signe]]]#place les apophones de V et C (resp. A et D)
            elif signe in "U":
                result=result+phonology["apophonies"][phonology["apophonies"][racine['V']]]	#place le bi-apophone de V
            else:
                result=result+signe
            if verbose: print signe, result
        if verbose: print result
        return result    
        result=forme

    typeTrans=""
    gabarit=re.match("^(\D*)(\d)(\D*)(\d)(\D*)(\d)(.*)$",transformation)
    if gabarit:
        racine=extraireRacine(forme)
        result=appliquerGabarit(transformation,racine)
        typeTrans="gabarit"
        if verbose: print "f,r,t",forme,racine,result
    else:
        affixe=re.match("^([^+]*)\+([^+]*)$",transformation)
        if affixe:
            if affixe.group(1)=="X":
                suffixe=affixe.group(2)
                result=forme+suffixe
                typeTrans="suffixe"
            elif affixe.group(2)=="X":
                prefixe=affixe.group(1)
                result=prefixe+forme
                typeTrans="préfixe"
        else:
            circonfixe=re.match("^([^+]*)\+([^+]*)\+([^+]*)$",transformation)
            if circonfixe:
                if circonfixe.group(2)=="X":
                    prefixe=circonfixe.group(1)
                    suffixe=circonfixe.group(3)
                    result=prefixe+forme+suffixe
                    typeTrans="circonfixe"
    return (result,typeTrans)

def modifierGlose(glose,sigma,typeTrans):
    '''
    Calcule la glose à partir de sigma
    '''
    mods=[]
    typeRef=(typeTrans=="ref")        
    attributValeurs=sigma.split(",")
    for attributValeur in attributValeurs:
            paire=attributValeur.split("=")
            if len(paire)==2:
                valeur=paire[1]
                if typeRef:
                    valeur=valeur.capitalize()
                mods.append(valeur)
    if typeRef:
        mod="".join(mods)
    else:
        mod=".".join(mods)
    if typeTrans=="gabarit":
        glose=glose+blanc("x"+mod)
    elif typeTrans=="suffixe":
        glose=glose+blanc("-"+mod)
    elif typeTrans=="préfixe":
        glose=blanc(mod+"-")+glose
    elif typeTrans=="circonfixe":
        glose=blanc(mod+"+")+glose+blanc("+"+mod)
    elif typeRef:
        glose="".join(glose.split(".")[0])+mod
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
        self.sets={}
        
    def addCategory(self,superclasse,classe):
        if not superclasse in self.classes:
            self.classes[superclasse]=[]
        self.classes[superclasse].append(classe)
        self.superieur[classe]=superclasse
        if superclasse in gloses:               #si superclasse est une catégorie
            self.categorie[classe]=superclasse
            category=superclasse
        else:                                   #si superclasse est une classe flexionnelle
            self.categorie[classe]=self.categorie[superclasse]
            category=self.categorie[superclasse]
        for element in self.sets[category]:
            for featureSet in element:
                for valeur in featureSet.split(","):
                    if classe == valeur:
                        hierarchieCF.addFeature(category,classe,element[featureSet])
    
    def addFeatureSet(self,category,attribute,values):
        if not category in self.sets:
            self.sets[category]=[]
        self.sets[category].append({values:attribute})
                
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
        return "%s:\t%s\t%s"%(self.sigma,self.forme, self.glose)
    
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
            cuts=self.nom.split(".")
            if len(cuts)>1:
                glose="%s\\blanc{.%s}"%(cuts[0],".".join(cuts[1:]))
            else:
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
        return self.stem+" :\n\t\t\t"+"\n\t\t\t".join(listCases)

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
        return "%s, %s, %s\n\t\t%s\n"%(self.stem,self.classe,self.nom,self.paradigme)
    
    def addForme(self,*formes):
        for forme in formes:
            self.formes.append(forme)
        
class Lexique:
    '''
    Lexique de Lexèmes
    '''
    def __init__(self):
        self.lexemes={}
        self.catLexeme={}
        
    def __repr__(self):
        return "\n".join(["%s :\n\t%s"%(cle,lexeme) for (cle,lexeme) in self.lexemes.iteritems()])
    
    def addLexeme(self,classe,stem,*formes):
        categorie=hierarchieCF.getCategory(classe)
        if classe!=categorie:
            nom=formes[0]+"."+classe
        else:
            nom=formes[0]
        self.lexemes[nom]=Lexeme(stem,classe,nom)
        self.lexemes[nom].addForme(*formes)
        if not categorie in self.catLexeme:
            self.catLexeme[categorie]=[]
        self.catLexeme[categorie].append(nom)
    
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


def analyserGloses(gloses):
    for category in gloses:
        if gloses[category]:
            for feature in gloses[category]:
                hierarchieCF.addFeatureSet(category,feature,",".join(gloses[category][feature]))

def analyserStems(niveau):
    for element in niveau:
        if depthDict(niveau[element])==1:
            for forme in niveau[element]:
                if isinstance(niveau[element][forme],str):
                    lexique.addLexeme(element,forme,niveau[element][forme])
                elif isinstance(niveau[element][forme],unicode):
                    lexique.addLexeme(element,forme,niveau[element][forme].encode('utf8'))
                elif isinstance(niveau[element][forme],list):
                    liste=[]
                    for f in niveau[element][forme]:
                        liste.append(f.encode("utf8"))
                    lexique.addLexeme(element,forme,*liste)
                else:
                    print "PB",element,forme,niveau[element][forme]
        else:
            for cle in niveau[element]:
                hierarchieCF.addCategory(element,cle)
            analyserStems(niveau[element])
    return