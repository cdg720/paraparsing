import csv
import sys
from CoNLL import Corpus

from preprocess import same

if len(sys.argv) != 5:
	print 'usage: python comp.py gold base dual .csv'
	sys.exit(0)

gold = Corpus(sys.argv[1]).sentences[::2]
base = Corpus(sys.argv[2]).sentences[::2]
dual = Corpus(sys.argv[3]).sentences[::2]

source = []
with open(sys.argv[4], 'rb') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	ind = 0
	for row in reader:
		ind += 1
		if ind % 3 == 1:
			source.append(row[0])

s_scores = {}
s_scores['QB'] = [0,] * 2
s_scores['BrownTune'] = [0,] * 2
s_scores['BNC'] = [0,] * 2
s_scores['WSJ24'] = [0,] * 2
b_scores = [0.] * 3
d_scores = [0.] * 3
board = [0] * 3
i = 0
duh = [0] * 5
for g, b, d, s in zip(gold, base, dual, source):
	tmp = b.evaluate(g)
	b_scores[0] += tmp[0]
	b_scores[1] += tmp[1]
	b_scores[2] += tmp[2]
	tmp2 = d.evaluate(g)	
	d_scores[0] += tmp2[0]
	d_scores[1] += tmp2[1]
	d_scores[2] += tmp2[2]
	if not same(b, d):
		duh[0] += 1
		if s == 'BNC':
			duh[1] += 1
		if s == 'BrownTune':
			duh[2] += 1
		if s == 'QB':
			duh[3] += 1
		if s == 'WSJ24':
			duh[4] += 1
	if tmp[0] > tmp2[0]: # lose
		board[2] += 1
		print  i, 'losing', tmp2[0] - tmp[0], s
		s_scores[s][1] += 1
	elif tmp[0] < tmp2[0]: # win
		board[0] += 1
		print i, 'winning', tmp2[0] - tmp[0], s
		s_scores[s][0] += 1		
	else:
		board[1] += 1 # tie
	i += 1

print board
print s_scores
print

print 'base'
print 'UAS: %d / %d * 100 = %.2f ' % (int(b_scores[0]), int(b_scores[2]), b_scores[0] / b_scores[2] * 100)
print 'LAS: %d / %d * 100 = %.2f' % (int(b_scores[1]), int(b_scores[2]), b_scores[1] / b_scores[2] * 100)
print
print 'dual'
print 'UAS: %d / %d * 100 = %.2f ' % (int(d_scores[0]), int(d_scores[2]), d_scores[0] / d_scores[2] * 100)
print 'LAS: %d / %d * 100 = %.2f' % (int(d_scores[1]), int(d_scores[2]), d_scores[1] / d_scores[2] * 100)

print duh
	
