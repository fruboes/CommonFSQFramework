#! /bin/bash

#proc=18
#mem=75GB
# -N 
#proc=30
#mem=120GB
proc=32
mem=100GB
#proc=25
#mem=80GB

echo "./do.py -c InclusiveBasic" | qsub  -V -l nodes=1:ppn=$proc -l mem=$mem -q local -d `pwd`
echo "./do.py -c MNWindow" | qsub  -V -l nodes=1:ppn=$proc -l mem=$mem -q local -d `pwd`
echo "./do.py -c MNBasic" | qsub  -V -l nodes=1:ppn=$proc -l mem=$mem -q local -d `pwd`
echo "./do.py -c MNAsym" | qsub  -V -l nodes=1:ppn=$proc -l mem=$mem -q local -d `pwd`
echo "./do.py -c InclusiveWindow" | qsub  -V -l nodes=1:ppn=$proc -l mem=$mem -q local -d `pwd`
echo "./do.py -c InclusiveAsym" | qsub  -V -l nodes=1:ppn=$proc -l mem=$mem -q local -d `pwd`
#echo "./do.py -c InclusiveAsym,InclusiveWindow,InclusiveBasic,MNBasic,MNAsym,MNWindow" | qsub  -V -l nodes=1:ppn=$proc -l mem=$mem -q local -d `pwd`
