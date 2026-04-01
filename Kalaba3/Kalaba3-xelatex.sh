#! /bin/bash

numeros="1 2 3 4 5"
texFiles=".tex -TD.tex -TD-Corr.tex -Rad.tex -Analyse.tex"

for numero in $numeros
do
for tex in $texFiles
    do
        cd /Users/gilles/sDrive/Cours/Bordeaux/L1-LinguistiqueGenerale/00-ProjetKalaba/24-K$numero
        xelatex K0$numero$tex
    done
done
