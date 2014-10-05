import csv
import numpy as np
import sys
from CoNLL import Corpus

if len(sys.argv) != 4:
	print 'usage: python analyze.py gold, pred, csv'
	print 'e.g.: python analyze.py ../data/dev1/gold.sd205 ../data/dev1/bllip.sd205 ../data/dev1/paraphrases.csv'
	sys.exit(0)

gold = Corpus(sys.argv[1]).sentences[::2]
pred = Corpus(sys.argv[2]).sentences[::2]

source = []
with open(sys.argv[3], 'rb') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	ind = 0
	for row in reader:
		ind += 1
		if ind % 3 == 1:
			source.append(row[0])

wsj24 = np.array([0,] * 3)
brown = np.array([0,] * 3)
bnc = np.array([0,] * 3)
qb = np.array([0,] * 3)
for g, p, s in zip(gold, pred, source):
	score = np.array(p.evaluate(g))
	if s == 'WSJ24':
		wsj24 += score
	elif s == 'BrownTune':
		brown += score
	elif s == 'BNC':
		bnc += score
	elif s == 'QB':
		qb += score
	else:
		print 'unknown source'

print 'WSJ24'
print 'UAS: %d / %d * 100 = %.2f ' % (wsj24[0], wsj24[2], float(wsj24[0]) / wsj24[2] * 100)
print 'LAS: %d / %d * 100 = %.2f' % (wsj24[1], wsj24[2], float(wsj24[1]) / wsj24[2] * 100)
print

print 'BrownTune'
print 'UAS: %d / %d * 100 = %.2f ' % (brown[0], brown[2], float(brown[0]) / brown[2] * 100)
print 'LAS: %d / %d * 100 = %.2f' % (brown[1], brown[2], float(brown[1]) / brown[2] * 100)
print

print 'BNC'
print 'UAS: %d / %d * 100 = %.2f ' % (bnc[0], bnc[2], float(bnc[0]) / bnc[2] * 100)
print 'LAS: %d / %d * 100 = %.2f' % (bnc[1], bnc[2], float(bnc[1]) / bnc[2] * 100)
print

print 'QB'
print 'UAS: %d / %d * 100 = %.2f ' % (qb[0], qb[2], float(qb[0]) / qb[2] * 100)
print 'LAS: %d / %d * 100 = %.2f' % (qb[1], qb[2], float(qb[1]) / qb[2] * 100)
