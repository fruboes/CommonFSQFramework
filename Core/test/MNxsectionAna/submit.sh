#! /bin/bash

echo "./do.py -c MNWindow" | qsub  -V -l nodes=1:ppn=40 -l mem=160GB -q local -d `pwd`
echo "./do.py -c MNBasic" | qsub  -V -l nodes=1:ppn=40 -l mem=160GB -q local -d `pwd`
echo "./do.py -c MNAsym" | qsub  -V -l nodes=1:ppn=40 -l mem=160GB -q local -d `pwd`
echo "./do.py -c InclusiveWindow" | qsub  -V -l nodes=1:ppn=40 -l mem=160GB -q local -d `pwd`
echo "./do.py -c InclusiveBasic" | qsub  -V -l nodes=1:ppn=40 -l mem=160GB -q local -d `pwd`
#echo "./do.py -c InclusiveBasic" | qsub  -V -l nodes=1:ppn=24 -l mem=96GB -q local -d `pwd`
#echo "./do.py -c InclusiveBasic" | qsub  -V -l nodes=1:ppn=12 -l mem=48GB -q local -d `pwd`
echo "./do.py -c InclusiveAsym" | qsub  -V -l nodes=1:ppn=40 -l mem=160GB -q local -d `pwd`
#echo "./do.py -c InclusiveAsym,InclusiveWindow,InclusiveBasic,MNBasic,MNAsym" | qsub  -V -l nodes=1:ppn=40 -l mem=160GB -q local -d `pwd`
