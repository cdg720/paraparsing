from bllipparser import RerankingParser, Tree
import csv
import sys

def best(sent):
	nbest_list = rrp.parse(sent)
	return nbest_list[0]

def nbest(sent):
	nbest_list = rrp.parse(sent)
	return nbest_list

if len(sys.argv) > 1 and sys.argv[1] == 'self':
	# self-trained
	path = '/pro/dpg/dc65/models/WSJ+Gigaword'
	print 'self-trained:', path
	rrp = RerankingParser.from_unified_model_dir(path)
else: 
	# bllip
	path = '/pro/dpg/dc65/models/WSJ'
	print 'basic:', path
	rrp = RerankingParser.from_unified_model_dir(path)

if len(sys.argv) < 2:
	print 'usage: python parse.py paraphrases.csv'
	sys.exit(0)
elif len(sys.argv) == 2 and sys.argv[1] == 'self':
	print 'usage: python parse.py self paraphrases.csv'
	sys.exit(0)

if len(sys.argv) == 3:
	path = sys.argv[2]
elif len(sys.argv) == 2:
	path = sys.argv[1]
else:
	print 'wrong'
	sys.exit(0)

mode = 1 # 0: gold, 1: 1best, 2: nbest
f = open('tmp/output', 'w')
if mode == 2:
	g = open('tmp/scores', 'w')
with open(path, 'rb') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	iter = 0
	for row in reader:
		iter += 1
		if iter % 3 == 1:
			if mode == 0:
				f.write(row[2] + '\n')
			elif mode == 1:
				words = Tree(row[2]).tokens() # pre-tokenized
				f.write(str(best(words).ptb_parse) + '\n')
			elif mode == 2:
				words = Tree(row[2]).tokens()
				nbest_list = nbest(words)
				g.write(str(len(nbest_list)) + '\n')
				for tree in nbest_list:
					f.write(str(tree.ptb_parse) + '\n')
					g.write(str(tree.parser_score) + '\t' + str(tree.reranker_score) + '\n')
			else:
				print 'plz'
		if iter % 3 == 2:
			if mode == 0 or mode == 1:
				f.write(str(best(row[3]).ptb_parse) + '\n')
			elif mode == 2:
				nbest_list = nbest(row[3])
				g.write(str(len(nbest_list)) + '\n')
				for tree in nbest_list:
					f.write(str(tree.ptb_parse) + '\n')
					g.write(str(tree.parser_score) + '\t' + str(tree.reranker_score) + '\n')
			else:
				print 'plz'
f.flush()
f.close()

	
        
        
