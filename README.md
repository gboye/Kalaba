#Kalaba
====

Outil de fabrication de Kalaba basé sur un lexique et un corpus de phrases préanalysées.

##Généralités
Dans l'ensemble des fichiers, les lignes commençant par un dièse sont considérées comme des commentaires. Elles ne sont pas prise en compte par l'outil.

##Phrases
Les phrases sont toutes construites sur le modèle Sujet Verbe COD COI Complément Circonstants. Les groupes sont séparés manuellement par des tabulations. Par exemple, pour la phrase simple Sujet-Verbe-COD comme "Le chasseur mange une autruche." :

le chasseur TAB mange TAB une autruche

Tous les mots qui sont utilisés dans les phrases doivent apparaître dans le lexique. Pour les mots français qui s'écrivent avec un -s final au singulier, il faut les écrire avec un -S majuscule pour que le système reconnaisse le mot comme singulier (pas de contrôle du nombre autre que graphique).

##Lexique
Le lexique est un fichier YAML qui utilise 4 catégories principales:
- nom : N
- verbe : V
- adjectif : ADJ
- déterminant : DET

Les catégories principales peuvent être organisées pour contenir des classes flexionnelles et des propriétés inhérentes. Par exemple, deux classes de noms avec 2 genres inhérents :

N:
  N1:
    Masc: 
      mak:  Marc
      toma: Thomas
    Fem:
      lusi: Lucie
      majo: Marion
    Neu: [classe,tableau]
  N2:
    Masc:
      jon:  John
      in:   Ian
    Fem: 
      beti: Betty
      Zon:  Joan

Dans la structure complète, le lexique doit donner un radical pour chaque élément et toutes les formes de l'élément susceptibles d'apparaître dans les phrases de la langue d'origine. Par exemple, pour les noms d'un kalaba sans classes flexionnelles ni genre inhérent :

N:
  buku:   [livre,livres]
  tabl:   [table, tables]
  tikus:  [souris]

##Gloses
Les gloses donnent la structure du paradigme flexionnel. Les attributs et leurs valeurs possibles sont définis pour chaque catégorie sujette à la flexion. Par exemple, pour un système simple avec du genre et du nombre pour les noms comme en français :

N:
  Genre: [M,F]
  Nombre: [SG, PL]

##Blocks
Ce fichier contient la description des blocs PFM pour les catégories du kalaba qui sont sujettes à la flexion. Aucun contrôle de cohérence n'est réalisé entre ce fichier et gloses.

Le fichier blocks donne pour chaque catégorie des blocs numérotés qui seront évalués dans l'ordre croissant des numéros. Au sein de chaque bloc, on trouve des règles de réalisation qui permettent de faire correspondre un ensemble de traits à une modification phonologique (préfixe, suffixe, circonfixe, gabarit). Une règle est applicable si elle concerne un lexème et une case du paradigme qui contiennent les traits mentionnés par la règle. Par exemple, pour un pluriel par suffixation en -s :

N:
  1:
    Nombre=PL: X+s

Les affixes sont notés :
  - X+affixe pour les suffixes
  - affixe+X pour les préfixes
  - affixe+X+affixe pour les circonfixes
Les gabarits sont notés avec 123 pour les trois consonnes de la racine (les trois premières consonnes, pas de contrôle), et V pour la voyelle radicale (la première voyelle, pas de contrôle). Par exemple, pour une forme de base comme ktab, on peut obtenir kattaba avec le gabarit suivant :

V:
  1:
    Type=Factitif, Pers=3, Genre=M: 1a22V3a

##Phonology
Ce fichier contient la description des éléments phonologiques et graphiques du kalaba.
