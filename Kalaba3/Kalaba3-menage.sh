#! /bin/bash

numeros="1 2 3 4 5"
extFiles="*.aux *.log"

for numero in $numeros
do
for ext in $extFiles
    do
        cd /Users/gilles/sDrive/Cours/Bordeaux/L1-LinguistiqueGenerale/00-ProjetKalaba/25-K$numero
        rm $ext
    done
done
