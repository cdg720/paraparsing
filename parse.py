from bllipparser import RerankingParser, Tree
import csv
import sys

def best(sent):
	nbest_list = rrp.parse(sent)
	#nbest_list = rrp.parse(sent, rerank=False) # HACK
	return nbest_list[0]

def nbest(sent):
	nbest_list = rrp.parse(sent)
	return nbest_list

if len(sys.argv) != 4:
	print 'usage: python parse.py paraphrases.csv mode parser'
	print 'usage: python parse.py paraphrases.csv 0 bllip'	
	sys.exit(0)

if sys.argv[3] == 'bllip':
	# bllip
	parser = '/pro/dpg/dc65/models/WSJ+QB'
	print 'basic:', parser
elif sys.argv[3] == 'self':
	# self-trained
	parser = '/pro/dpg/dc65/models/WSJ+Gigaword'
	print 'self-trained:', parser
else:
	print 'parser options: bllip, self'
	sys.exit(0)

rrp = RerankingParser()
rrp.load_parser_model(parser + '/parser')
print 'reranker: /pro/dpg/dc65/models/WSJ/'
rrp.load_reranker_model('/pro/dpg/dc65/models/WSJ/reranker/features.gz', '/pro/dpg/dc65/models/WSJ/reranker/weights.gz')
	
mode = int(sys.argv[2]) # 0: gold, 1: 1best, 2: nbest
f = open('tmp/trees', 'w')
if mode == 2:
	g = open('tmp/scores', 'w')
with open(sys.argv[1], 'rb') as csvfile:
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

	
        
        
