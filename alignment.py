#!bin/python3

from Bio import Align
from Bio.Seq import Seq
 
x1='General Medicine'
x2='General Medicine'
x3='GeneralMedicine'  #if new line at end of word
x4='General ediine' #if new line in between word
x5='General Surgery' #if new line in between word
x6='Plastic Surgery' #if new line in between word
x7='Emergency Medicine' #if new line in between word

aligner = Align.PairwiseAligner()
print(aligner)
alignments = aligner.align(x1,x2)
print(alignments[0])
score = aligner.score(x1,x2)
print(score)

alignments = aligner.align(x1,x3)
print(alignments[0])
score = aligner.score(x1,x3)
print(score)

alignments = aligner.align(x1,x4)
print(alignments[0])
score = aligner.score(x1,x4)
print(score)

alignments = aligner.align(x1,x5)
print(alignments[0])
score = aligner.score(x1,x5)
print(score)

alignments = aligner.align(x1,x6)
print(alignments[0])
score = aligner.score(x1,x6)
print(score)


alignments = aligner.align(x1,x7)
print(alignments[0])
score = aligner.score(x1,x7)
print(score)
