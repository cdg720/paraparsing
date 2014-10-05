import sys
from CoNLL import Corpus

if len(sys.argv) != 3:
	print 'usage: python eval.py gold pred'
	print 'e.g.: python eval.py ../data/dev1/gold.sd205 ../data/dev1/dual3.logit2'
	sys.exit(0)

gold = Corpus(sys.argv[1]).sentences[::2]
pred = Corpus(sys.argv[2]).sentences[::2]

scores = [0.,] * 3
for g, p in zip(gold, pred):
	tmp = p.evaluate(g)
	scores[0] += tmp[0]
	scores[1] += tmp[1]
	scores[2] += tmp[2]
print 'UAS: %d / %d * 100 = %.2f ' % (int(scores[0]), int(scores[2]), scores[0] / scores[2] * 100)
print 'LAS: %d / %d * 100 = %.2f' % (int(scores[1]), int(scores[2]), scores[1] / scores[2] * 100)

