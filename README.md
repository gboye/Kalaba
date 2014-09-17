#Kalaba
====

Outil de fabrication de Kalaba basé sur un lexique et un corpus de phrases préanalysées.

##Généralités
Dans l'ensemble des fichiers, les lignes commençant par un dièse sont considérées comme des commentaires. Elles ne sont pas prise en compte par l'outil.

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

##Phrases
Les phrases sont toutes construites sur le modèle Sujet Verbe COD COI Complément Circonstants. Les groupes sont séparés manuellement par des tabulations. Par exemple, pour la phrase simple Sujet-Verbe-COD comme "Le chasseur mange une autruche." :

le chasseur TAB mange TAB une autruche
