# coding: utf-8
import re, warnings
import pandas as pd

gloses={}
phonology={}
morphosyntax={}
categoriesMajeures=["VER","NOM","ADJ"]
categoriesMineures=["PREP","DET"]
verbose=False

def chaine2utf8(chaine):
    if type(chaine)==str:
        result=unicode(chaine.decode('utf8'))
    elif type(chaine)==unicode:
        result=chaine
    return result


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

def cacherGloses(chaine):
    return u"\\cacherGloses{"+chaine+"}"

def modifierForme(forme,formeDecoupe,transformation):
    def extraireRacine(simple):
        if verbose: print "simple : ", simple
        c=1
        result={'1':'','2':'','3':'','V':''}
        for lettre in simple:
            if verbose: print "lettre : ",lettre
            if lettre in phonology["consonnes"]:
                if c<=3:
                    result[str(c)]=lettre
                c=c+1
            elif lettre in phonology["voyelles"]:
                if result['V']=='':
                    result['V']=lettre
            else:
                if verbose: print "erreur sur racine", simple
        if result["2"]=="":
            result["2"]=result["1"]
        if result["3"]=="":
            result["3"]=result["2"]
        if result["V"]=="":
            result["V"]="a"
        return result

    def appliquerGabarit(forme,racine,sansRacine=True):
        '''
        met la racine dans le gabarit forme
        '''
        if verbose: print "gabarit : ", forme, racine
        result=""
        for signe in forme:
            if signe in "123":				#place les consonnes en 1, 2, 3
                if sansRacine:
                    result=result+racine[signe]
                else:
                    result=result+u"\\textRacineC{%s}"%racine[signe]
            elif signe in "456":
                result=result+phonology["mutations"][racine[str(int(signe)-3)]]
            elif signe in "789":
                result=result+phonology["mutations"][phonology["mutations"][racine[str(int(signe)-6)]]]
            elif signe in "V":				#place la voyelle radicale V et la voyelle de classe C
                if sansRacine:
                    result=result+racine[signe]
                else:
                    result=result+u"\\textRacineV{%s}"%racine[signe]
            elif signe in "A":
                result=result+phonology["apophonies"][racine[phonology["derives"][signe]]]#place les apophones de V et C (resp. A et D)
            elif signe in "U":
                result=result+phonology["apophonies"][phonology["apophonies"][racine['V']]]	#place le bi-apophone de V
            else:
                result=result+signe
            if verbose: print signe, result
        if verbose: print result
        return result
#        result=forme

    typeTrans=""
    lexRacine=""
    gabarit=re.match(u"^(\D*)(\d)(\D*)(\d)(\D*)(\d)?(.*)$",transformation)
    if gabarit:
        if forme.startswith(u"\\textRadical{"):
            radical=forme.split("{")[1].strip("}")
            racine=extraireRacine(radical)
            sansRacine=False
        else:
            racine=extraireRacine(forme)
            sansRacine=True
        result=appliquerGabarit(transformation,racine,sansRacine)
        typeTrans="gabarit"
        decoupe=u"racine(%s)x%s"% (formeDecoupe,transformation)
        lexRacine=racine["1"]+racine["2"]+racine["3"]+racine["V"]
        if verbose: print "f,r,t",forme,racine,result
    else:
        affixe=re.match(u"^([^+]*)\+([^+]*)$",transformation)
        if affixe:
            if affixe.group(1)=="X":
                suffixe=affixe.group(2)
                result=forme+suffixe
                typeTrans="suffixe"
                decoupe=u"%s-%s"%(formeDecoupe,suffixe)
            elif affixe.group(2)=="X":
                prefixe=affixe.group(1)
                result=prefixe+forme
                typeTrans="préfixe"
                decoupe=u"%s-%s"%(prefixe,formeDecoupe)
        else:
            circonfixe=re.match(u"^([^+]*)\+([^+]*)\+([^+]*)$",transformation)
            if circonfixe:
                if circonfixe.group(2)=="X":
                    prefixe=circonfixe.group(1)
                    suffixe=circonfixe.group(3)
                    result=prefixe+forme+suffixe
                    typeTrans="circonfixe"
                    decoupe=u"%s+%s+%s"%(prefixe,formeDecoupe,suffixe)
            else:
#                print "affixe nul", forme, formeDecoupe
                result=forme
                typeTrans="identite"
                decoupe=formeDecoupe
    return (result,decoupe,typeTrans,lexRacine)

def modifierGlose(glose,sigma,typeTrans):
    '''
    Calcule la glose à partir de sigma
    '''
    mods=[]
    typeRef=(typeTrans=="ref")
    attributValeurs=sigma.split(",")
    for attributValeur in attributValeurs:
            if verbose: print attributValeur,
            paire=[x.strip() for x in attributValeur.split("=")]
            if len(paire)==2:
                valeur=paire[1]
                if not typeRef:
                    mods.append(valeur)
                elif paire[0]!="CF":
                    valeur=valeur.capitalize()
                    mods.append(valeur)
    if verbose: print
    if typeRef:
        mod="".join(mods)
    else:
        mod=".".join(mods)
    if typeTrans=="gabarit":
        glose=glose+cacherGloses("x"+mod)
    elif typeTrans=="suffixe":
        glose=glose+cacherGloses("-"+mod)
    elif typeTrans=="préfixe":
        glose=cacherGloses(mod+"-")+glose
    elif typeTrans=="circonfixe":
        glose=cacherGloses(mod+"+")+glose+cacherGloses("+"+mod)
    elif typeRef:
        glose="".join(glose.split(".")[0])+mod
        # modification à faire pour HYPER pour les noms de mêmes genres
        # abandonnée pour l'instant
        # if "hyper" in glose.lower():
        #     glose="".join(glose.split(".")[0])+"HYPER"+mod
        # else:
        #     glose="".join(glose.split(".")[0])+mod
    return glose

class DuplicateForm(Exception):
    pass

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

    def getSigmas(self,classes):
#        print "getSig", classe
        sigmas=[]
        CF=""
        filtre=""
        for classe in classes:
            if classe in hierarchieCF.categorie:
                cat=hierarchieCF.categorie[classe]
                feature=hierarchieCF.getFeature(cat,classe)
    #            filtre="%s=%s"%(feature,classe)
                if feature=="CF":
                    CF+="CF="+classe+", "
                else:
                    filtre+="%s=%s"%(feature,classe)
            else:
                cat=classe
    #        print "cat",cat,sigmas
        if cat in self.cases:
            for element in self.cases[cat]:
                for cle in element:
                    if filtre in cle:
                        if CF!="":
                            morceaux=cle.split(",")
                            cle=morceaux[0]+", "+CF+",".join(morceaux[1:])
                        sigmas.append(cle)
#            print sigmas
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
        self.inherents={}

    def addCategory(self,superclasse,classe):
        if not superclasse in self.classes:
            self.classes[superclasse]=[]
        self.classes[superclasse].append(classe)
        self.superieur[classe]=superclasse
        if superclasse in gloses:               #si superclasse est une catégorie
            self.categorie[classe]=superclasse
            if not superclasse in self.inherents:
                self.inherents[superclasse]=[]
            if not classe in self.inherents[superclasse]:
                self.inherents[superclasse].append(classe)
            category=superclasse
        else:                                   #si superclasse est une classe flexionnelle
            self.categorie[classe]=self.categorie[superclasse]
            if not classe in self.inherents[self.categorie[classe]]:
                self.inherents[self.categorie[classe]].append(classe)
            category=self.categorie[superclasse]
        noFeature=True
        for element in self.sets[category]:
            for featureSet in element:
                for valeur in featureSet.split(","):
                    if classe == valeur:
                        hierarchieCF.addFeature(category,classe,element[featureSet])
                        noFeature=False
        if noFeature:
            hierarchieCF.addFeature(category,classe,"CF")

    def addFeatureSet(self,category,attribute,values):
        if not category in self.sets:
            self.sets[category]=[]
        self.sets[category].append({values:attribute})

    def addFeature(self,category,classe,feature):
        if not category in self.trait:
            self.trait[category]=[]
        if not {classe:feature} in self.trait[category]:
            self.trait[category].append({classe:feature})

    def getFeature(self,category,classe):
        if category in self.trait:
            return [x for x in self.trait[category] if classe in x.keys()][0][classe]
        else:
            return "ClassFLex"

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
    def __init__(self,sigma,forme,glose,decoupe,detoure,lexRadical,lexRacine):
        self.sigma=sigma
        self.forme=forme
        self.glose=glose
        self.decoupe=decoupe
        self.detoure=detoure
        self.radical=lexRadical
        self.racine=lexRacine

    def __repr__(self):
        return u"%s:\t%s\t%s\t%s\t%s\tradical: %s\tracine: %s"%(self.sigma,self.forme, self.glose, self.decoupe, self.detoure,self.radical,self.racine)

class Tableau:
    '''
    liste de sigmas
    '''
    def __init__(self,classe,stem,nom):
#        print "initTableau",classe, stem, nom
        self.cases=[]
        self.stem=stem
        self.nom=nom
        classes=classe.split(".")
        categorie=hierarchieCF.getCategory(classes[0])
        for case in paradigmes.getSigmas(classes):
            forme=self.stem
            cuts=self.nom.split(".")
            if len(cuts)>1:
                glose=cuts[0]+cacherGloses("."+".".join(cuts[1:]))
            else:
                glose=self.nom
            derivations=regles.getRules(categorie,case)
            decoupe=forme
            radical=u"\\textRadical{%s}"%forme
            detoure=forme
            lexRacine=""
            if derivations:
                for derivation in derivations:
                    (radical,detoure,operation,tmpRacine)=modifierForme(radical,detoure,derivation[0])
                    (forme,decoupe,operation,tmpRacine)=modifierForme(forme,decoupe,derivation[0])
                    if lexRacine=="":
                        lexRacine=tmpRacine
                    glose=modifierGlose(glose,derivation[1],operation)
            flexion=Forme(case,forme,glose,decoupe,radical,self.stem,lexRacine)
            self.cases.append(flexion)

    def __repr__(self):
        listCases=[]
        for case in self.cases:
            print u"case", case, case.racine
            listCases.append(unicode(case))
        return self.stem+u" :\n\t\t\t"+u"\n\t\t\t".join(listCases)

class Lexeme:
    '''
    Formes fléchies d'un lexème suivant sa classe flexionnelle
    '''
    def __init__(self,stem,classe,nom):
        self.stem=stem
        self.classe=classe
        self.nom=nom
        if classe in categoriesMineures:
#            self.nom=self.nom.decode('utf8').upper().encode('utf8')
            self.nom=chaine2utf8(self.nom).upper()
        self.paradigme=Tableau(classe,stem,nom)
        self.formes=[]

    def __repr__(self):
        return u"%s, %s, %s\n\t\t%s\n"%(self.stem,self.classe,self.nom,self.paradigme)

    def addForme(self,*formes):
        for forme in formes:
            self.formes.append(forme)

    def getParadigm(self,lignes=[],colonne=[]):
        formeLignes=self.paradigme.cases
        #print "======Paradigme======="
        unTraits=[t.strip() for t in formeLignes[0].sigma.split(",")[1:]]
        onTraits=[unTraits[i].split("=")[0].strip() for i in range(len(unTraits)) if not unTraits[i].strip().startswith("CF=")]
        formesFlechies=pd.DataFrame(columns=onTraits+["forme"])
        for n,l in enumerate(formeLignes):
            ulTraits=l.sigma.split(",")[1:]
            olTraits=[ulTraits[i].split("=")[1] for i in range(len(ulTraits)) if not ulTraits[i].strip().startswith("CF=")]
            formesFlechies.loc[n]=olTraits+[l.decoupe]
        if not lignes:
            lignes=onTraits[:-1]
        if not colonne:
            colonne=onTraits[-1:]
        for trait in onTraits:
           if not trait in lignes+colonne:
               print "del",trait
               formesFlechies.drop(trait, axis=1, inplace=True)
        formesFlechies.drop_duplicates(inplace=True)
        #print formesFlechies.columns, lignes, colonne
        tableParadigme=pd.pivot_table(formesFlechies,index=lignes,columns=colonne,values="forme",aggfunc=lambda x: ",".join(list(set(x))))
        return tableParadigme

duplicateErrors=[]
class Lexique:
    '''
    Lexique de Lexèmes
    '''
    def __init__(self):
        self.lexemes={}
        self.catLexeme={}
        self.formeLexeme={}
        self.formesFr={}
        self.vedettes={}

    def __repr__(self):
        return u"\n".join([u"%s :\n\t%s"%(cle,lexeme) for (cle,lexeme) in self.lexemes.iteritems()])

    def addLexeme(self,head,classe,stem,*tupleFormes):
#        print "addLex",head,classe,stem
#Mise en minuscules des formes de citations sauf initiale
        formes=list(tupleFormes)
        for forme in formes:
            if forme in self.formesFr:
                print forme,formes[0],self.formesFr[forme]
                warnings.warn(u'Formes homographes "%s" pour "%s" et "%s"'%(forme,formes[0],self.formesFr[forme]),stacklevel=0)
                duplicateErrors.append(u'Formes homographes "%s" pour "%s" et "%s"'%(forme,formes[0],self.formesFr[forme]))
            else:
                self.formesFr[forme]=formes[0]
        if formes[0]!=formes[0].upper() and formes[0]!=formes[0].lower():
            formes[0]=formes[0][0]+formes[0][1:].lower()
        cfs=head.split(",")
        if len(cfs)>2:
            classesFlex=".".join(cfs[2:])+"."+classe
        else:
            classesFlex=classe
        categorie=hierarchieCF.getCategory(classe)
        if classe!=categorie:
            nom=formes[0]+"."+classesFlex
        else:
            nom=formes[0]
        if formes[0] in self.vedettes:
            if self.vedettes[formes[0]]!=nom:
                warnings.warn(u'Vedettes homographes "%s" pour "%s" et "%s"'%(formes[0],self.vedettes[formes[0]],nom))
        else:
            self.vedettes[formes[0]]=nom
        self.lexemes[nom]=Lexeme(stem,classesFlex,nom)
        self.lexemes[nom].addForme(*formes)
        for forme in formes:
            if not forme in self.formeLexeme:
                self.formeLexeme[forme]=[]
            self.formeLexeme[forme].append(nom)
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
                        # modification pour les disjonctions
                        # 03/09/18
                        m=re.match(ur"(.*=)(.*)",trait)
                        if m:
                            altTrait=m.group(1)
                            altValeurs=m.group(2).split("|")
                            if verbose: print altTrait
                            altTraits=[altTrait+v for v in altValeurs]
                            if verbose: print altTraits
                            if any(t in case for t in altTraits):
                                if verbose: print "applies",case
                                caseMatch=True
                            else:
                                if verbose: print "does not apply",case
                                caseMatch=False
                        sigmaCase=sigmaCase and caseMatch
                        # fin de modification
                        # ancienne ligne
                        #
                        # sigmaCase=sigmaCase and trait in case
                    if sigmaCase:
                        rules.append((self.blocs[category][num][sigma],sigma))
                        break
            return rules
        else:
            return []

regles=Regles()


def analyserGloses(gloses):
    for category in gloses:
#        print category
        if gloses[category]:
            features=gloses[category].keys()
            featuresOrdre=morphosyntax["Attributs"][category]
            if set(features)|set(featuresOrdre)!=set(featuresOrdre):
                print "Incohérence entre Gloses.yaml et Morphosyntax.yaml"
            print category,":",
            for feature in featuresOrdre:
                if feature in features:
                    print feature,
                    hierarchieCF.addFeatureSet(category,feature,",".join(gloses[category][feature]))
            print

def analyserStems(niveau,head="stems"):
    '''
    alimentation du lexique et analyse de la flexion inhérente
    '''
    print "head",head
    for element in niveau:
        if depthDict(niveau[element])==1:
            if verbose: print "niveau1",element,niveau[element]
            for forme in niveau[element]:
#                 if isinstance(niveau[element][forme],str):
#                     lexique.addLexeme(head,element,forme,niveau[element][forme])
#                 elif isinstance(niveau[element][forme],unicode):
#                     lexique.addLexeme(head,element,forme,niveau[element][forme].encode('utf8'))
#                 elif isinstance(niveau[element][forme],list):
#                     liste=[]
#                     for f in niveau[element][forme]:
#                         liste.append(f.encode("utf8"))
#                     lexique.addLexeme(head,element,forme,*liste)
#                 else:
#                     print "PB",element,forme,niveau[element][forme]
                if isinstance(niveau[element][forme],str):
                    lexique.addLexeme(head,element,forme,chaine2utf8(niveau[element][forme]))
                elif isinstance(niveau[element][forme],unicode):
                    lexique.addLexeme(head,element,forme,chaine2utf8(niveau[element][forme]))
                elif isinstance(niveau[element][forme],list):
                    liste=[]
                    for f in niveau[element][forme]:
                        liste.append(chaine2utf8(f))
                    lexique.addLexeme(head,element,forme,*liste)
                else:
                    print "PB",element,forme,niveau[element][forme]
        else:
            if verbose: print "autres niveaux",element,niveau[element]
            for cle in niveau[element]:
                if verbose: print "addCat", element,cle
                hierarchieCF.addCategory(element,cle)
            analyserStems(niveau[element],head+","+element)
    return
