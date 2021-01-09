#! /bin/bash

numeros="1 2 3 4 5"
texFiles=".tex -TD.tex -TD-Corr.tex -Analyse.tex"

for numero in $numeros
do
for tex in $texFiles
    do
        cd /Users/gilles/ownCloud/Cours/Bordeaux/L1-LinguistiqueGenerale/00-ProjetKalaba/20-K$numero
        xelatex K$numero$tex
    done
done
