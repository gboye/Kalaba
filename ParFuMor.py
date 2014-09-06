# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Partie 0. Préparation

# <codecell>

import re
import sys
import codecs

# <headingcell level=2>

# fichiers

# <codecell>

# ouvre le fichier de règles (Kalaba-Gloses.txt)
try:
    regles=codecs.open(sys.argv[1],"r", "utf-8")
except IOError:
    print ('le fichier "'+ sys.argv[1]+ '" ne peut pas être ouvert')
    sys.exit()

# ouvre le fichier du lexique (Kalaba-Stems.txt)
try:
    lexique=codecs.open(sys.argv[2],"r", "utf-8")
except IOError:
    print ('le fichier "'+ sys.argv[2]+ '" ne peut pas être ouvert')
    sys.exit()
    
# ouvre le fichier des blocs (blocks.txt)
try:
    blocks_file=codecs.open(sys.argv[3],"r", "utf-8")
except IOError:
    print ('le fichier "'+ sys.argv[3]+ '" ne peut pas être ouvert')
    sys.exit()

# <codecell>

#regles = !cat Kalaba-Gloses.txt

# <codecell>

#lexique = !cat ./Kalaba-Stems.txt

# <codecell>

#blocks_file = !cat ./blocks.txt

# <headingcell level=2>

# fonctions

# <codecell>

def merge_2_lists(liste1, liste2):
    """
    Fusionne deux listes. 
    prend en argument deux listes
    """
    for l in range(1):
        temp = []
        for i in liste1:
            for j in liste2:
                temp.append(i+j)
        return temp

# <codecell>

def merge_lists(liste):
    """
    Fusionne autant de listes qu'il y a de cas de figure prévus
    prend en argument une liste de listes
    utilise merge_2_lists()
    Pour étendre la fonction, observer les deux premières boucles.
    """
    if len(liste) == 2:
        listea = merge_2_lists(liste[0], liste[1])
        return listea
    elif len(liste) == 3:
        listea = merge_2_lists(liste[0], liste[1])
        listeb = merge_2_lists(listea, liste[2])
        return listeb
    elif len(liste) == 4:
        listea = merge_2_lists(liste[0], liste[1])
        listeb = merge_2_lists(listea, liste[2])
        listec = merge_2_lists(listeb, liste[3])
        return listec
    elif len(liste) == 5:
        listea = merge_2_lists(liste[0], liste[1])
        listeb = merge_2_lists(listea, liste[2])
        listec = merge_2_lists(listeb, liste[3])
        listed = merge_2_lists(listec, liste[4])
        return listed
    else:
        print("il y a trop de listes à fusionner.\nveuillez étendre la fonction merge_lists()")

# <codecell>

def order(liste):
    """
    compte le nombre de traits (ajoute le tuple (nombre_de_traits, ligne) à ordered_tuples[] )
    ordonne la liste en ordre descendant
    renvoie la liste des lignes en ordre descendant
    """
    ordered_tuples = []
    ordered = []
    for l in liste:
        splitted = len(l.split(", "))
        ordered_tuples.append((splitted, l))
    ordered_tuples.sort(reverse=True)
    
    for o in ordered_tuples:
        ordered.append(o[1])
    return ordered

# <headingcell level=1>

# Partie 1 : générer les "commandes"

# <headingcell level=2>

# générer le paradigme vide

# <rawcell>

# pour chaque ligne dans paradigme:
#     si la ligne n'est pas vide,:
#         # gestion de la première ligne : catégorie grammaticale
#         si il y a ":" dans la ligne, on met la catégorie dans une liste qu'on ajoute à lists[]
#         # gestion des lignes du genre de "Nombre"
#         si il y a ";" dans la ligne:
#             on découpe la ligne sur les \t, puis sur les ;
#             pour chaque côté du ; on découpe sur les . puis les , et on génère tous les cas de figure.
#             on ajoute tout ça dans lists[]
# 
#             

# <codecell>

paradigme = []
lists = []
for r in regles:
    r=r.strip()
    # gestion de la première ligne : catégorie grammaticale
    if r != "=":
        if ":" in r:
            temp_list = []
            r = re.sub(":", "", r)
            temp_list.append(r.strip())
            lists.append(temp_list)
        elif "\t" in r:
            temp_list = []
            split1 = r.split("\t")
            split2 = split1[1].split(",")
            for s in split2:
                temp_list.append(", "+split1[0]+"="+s.strip())
            lists.append(temp_list)
    elif "=" in r:
        paradigme.extend(merge_lists(lists)) 
        lists = []  

# <codecell>

#for o in paradigme:
#    print(o)

# <headingcell level=2>

# Générer le paradigme de chaque lexème

# <markdowncell>

# structure d'une commande : 
# forme;cat-gram;attr;valeur

# <codecell>

lex = []
cat_lex = ""
temp_list = []
traduction = {} # dictionnaire pour retrouver la traduction lors de la génération des formes fléchies
for l in lexique:
    l=l.strip()
    # extraction de la catégorie grammaticale du des lexèmes
    if l.startswith("# "):
        cat_lex = re.sub("# ", "", l)
        if len(temp_list) != 0:
            lex.extend(temp_list)
        temp_list = []
    elif "," in l:
        champs = l.split(",")
        traduction[champs[1]]=champs[2]
        for p in paradigme:
            catgram = p.split(", ")
            # si la categorie dans lexique[] correspond à celle dans paradigme[]
            if catgram[0] == cat_lex:
                for c in catgram:
                    if "=" in c:
                        trait = c.split("=")
                        # si la valeur du trait que le lexème choisi (ex M,F,A,I pour un N)
                        # est la valeur d'un des traits de la ligne, on ajoute phono+ligne dans lex[]
                        if trait[1] == champs[0]:
                            traits = " ".join(catgram)
                            temp_list.append(champs[1]+", "+p)

# <codecell>

#for l in lex:
#    print(l)

# <headingcell level=1>

# Partie 2 : Importer les blocks

# <codecell>

blocks = []
lists = []
cat_block = ""
for b in blocks_file:
    b=b.strip()
    # gestion de la première ligne : catégorie grammaticale
    if b != "=":
        if ":" in b:
            b = b.split("-")
            b = b[0].strip()
            cat_block = b
        else:
            lists.append(b)
    elif "=" in b: 
        blocks.append((cat_block, order(lists)))
        lists = []

# <codecell>

#for b in blocks:
#    print(b)

# <headingcell level=1>

# Partie 3 : générer les formes fléchies

# <codecell>

output = []
for l in lex:
    modified = l.split(", ")
    traits_lexeme = l.split(", ")[2:]
    for b in blocks:
        if l.split(", ")[1] == b[0]:
            a = False # False = règle du block pas encore appliquée
            for c in b[1]:
                splitted = c.split(" > ")
                ajout = splitted[1]
                traits_block = splitted[0].split(", ")
                if a == False and len(list(set(traits_block+traits_lexeme))) <= len(traits_lexeme) or len(list(set(traits_block+traits_lexeme))) <= len(traits_block):
                    a = True
                    modified[0] += ajout
    form = modified[0]                             # forme fléchie
    francais = traduction[l.split(", ")[0]]   # traduction en français
    categ = modified[1]                            # catégorie grammaticale
    traits_str = ", ".join(modified[2:])           # liste des traits joints par ", "
    ### insérer ci-dessous la mise en page 
    commande1 = "<A>"+form+"\t\t\t"+categ+" , "+traits_str+"</A>"
    commande2 = "<B>\t\t"+francais+"\t"+categ+" , "+traits_str+"</B>\n"
    ###
    output.append(commande1)
    output.append(commande2)

# <codecell>

#for o in output:
#    print(o)

# <codecell>

# écrit le paradigme fléchi dans un fichier
with open("paradigme_fléchi.txt", "a") as f:
    for o in output:
        f.write(o)
        f.write("\n")

# <codecell>


