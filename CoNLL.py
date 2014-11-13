import gzip
import sys
import re

class Corpus:
	def __init__(self, file):
		self.read_file(file)

	def read_file(self, file):
		self.sentences = []
		if file.endswith('.gz'):
			f = gzip.open(file, 'rb')
		else:
			f = open(file, 'r')
		tokens = []
		for line in f.read().splitlines():
			line = line.strip()
			if line == '':
				self.sentences.append(Sentence(tokens))
				tokens = []
				continue
			items = line.split('\t')
			if len(items) != 8 and len(items) != 10:
				print 'Wrong Format'
				print line
				sys.exit(0)
			tokens.append(Token(items))
		if tokens: # not empty
			self.sentences.append(tokens)

class Sentence:
	def __init__(self, tokens):
		root = Token(['0','ROOT','_','_','_','_','-1','_','_','_'])
		self.tokens = [root] + tokens
		self.score = None

	def __len__(self):
		return len(self.tokens)

	def __str__(self):
		tmp = ''
		for i in xrange(1, len(self)): # exclude ROOT
			tmp += str(self.tokens[i].id) + '\t' + self.tokens[i].form + '\t' + self.tokens[i].lemma + '\t' + self.tokens[i].cpos + '\t' + self.tokens[i].pos + '\t' + self.tokens[i].feat + '\t' + str(self.tokens[i].head) + '\t' + self.tokens[i].deprel + '\t_\t_\n'
		return tmp

	def evaluate(self, gold):
		regex = re.compile(r'^[-!"#%&\'()*,./:;?@[\\\]_{}]+$')
		#etc = ['-LRB-', '-RRB-', '``']
		etc = []
		if len(self) != len(gold):
			print [x.form for x in self.tokens]
			print [x.form for x in gold.tokens]
			sys.exit(0)
		score = [0,] * 3;
		for token1, token2 in zip(self.tokens, gold.tokens):
			if token1.head == -1: # head
				continue
			# if token1.form != token2.form:
			# 	print [x.form for x in self.tokens]
			# 	print [x.form for x in gold.tokens]
			# 	sys.exit(0)
			if not regex.match(token1.form) and token1.form not in etc:
				score[2] += 1
				if token1.head == token2.head:
					score[0] += 1
					if token1.deprel == token2.deprel:
						score[1] += 1
		return score

	def words(self):
		return [x.form for x in self.tokens]

# CoNLL 2006 English
class Token:
	def __init__(self, items):
		self.id = int(items[0]) # int
		self.form = items[1]
		self.lemma = items[2]
		self.cpos = items[3]
		self.pos = items[4]        
		self.feat = items[5]
		self.head = int(items[6]) # int
		self.deprel = items[7]

# def main():
# 	corpus = Corpus('output.sd205')
# 	print len(corpus.sentences)
# 	for sent in corpus.sentences:
# 		print sent
# 	# print ' '.join([x.form for x in corpus.sentences[0].tokens])
# 	# print ' '.join([x.form for x in corpus.sentences[-2].tokens])

# main()
