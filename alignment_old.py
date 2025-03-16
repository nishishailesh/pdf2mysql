#!bin/python3

from Bio import pairwise2
#Bio.Align.PairwiseAligner
from Bio.pairwise2 import format_alignment


x1='General Medicine'
x2='General Medicine'
x3='GeneralMedicine'  #if new line at end of word
x4='General ediine' #if new line in between word

alignments = pairwise2.align.globalxx(x1,x2)
print(format_alignment(*alignments[0]))


alignments = pairwise2.align.globalxx(x1,x3)
print(format_alignment(*alignments[0]))


alignments = pairwise2.align.globalxx(x1,x4)
print(format_alignment(*alignments[0]))
