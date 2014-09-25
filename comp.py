import sys
from CoNLL import Corpus

if len(sys.argv) != 4:
	print 'usage: python comp.py gold base dual'
	sys.exit(0)

gold = Corpus(sys.argv[1]).sentences[::2]
base = Corpus(sys.argv[2]).sentences[::2]
dual = Corpus(sys.argv[3]).sentences[::2]

b_scores = [0.] * 3
d_scores = [0.] * 3
board = [0] * 3
i = 0
for g, b, d in zip(gold, base, dual):
	tmp = b.evaluate(g)
	b_scores[0] += tmp[0]
	b_scores[1] += tmp[1]
	b_scores[2] += tmp[2]
	tmp2 = d.evaluate(g)	
	d_scores[0] += tmp2[0]
	d_scores[1] += tmp2[1]
	d_scores[2] += tmp2[2]
	if tmp[0] > tmp2[0]: # lose
		board[2] += 1
		print  i, 'losing', tmp2[0] - tmp[0]		
	elif tmp[0] < tmp2[0]: # win
		board[0] += 1
		print i, 'winning', tmp2[0] - tmp[0]
	else:
		board[1] += 1 # tie
	i += 1

print board
print

print 'base'
print 'UAS: %d / %d * 100 = %.2f ' % (int(b_scores[0]), int(b_scores[2]), b_scores[0] / b_scores[2] * 100)
print 'LAS: %d / %d * 100 = %.2f' % (int(b_scores[1]), int(b_scores[2]), b_scores[1] / b_scores[2] * 100)
print
print 'dual'
print 'UAS: %d / %d * 100 = %.2f ' % (int(d_scores[0]), int(d_scores[2]), d_scores[0] / d_scores[2] * 100)
print 'LAS: %d / %d * 100 = %.2f' % (int(d_scores[1]), int(d_scores[2]), d_scores[1] / d_scores[2] * 100)
	
	