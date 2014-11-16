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

		self.regex = re.compile(r'^[-!"#%&\'()*,./:;?@[\\\]_{}]+$')
		self.etc = ['-LRB-', '-RRB-', '``']
		#self.etc = ['-LRB-', '-RRB-']
		

	def __len__(self):
		return len(self.tokens)

	def __str__(self):
		tmp = ''
		for i in xrange(1, len(self)): # exclude ROOT
			tmp += str(self.tokens[i].id) + '\t' + self.tokens[i].form + '\t' + self.tokens[i].lemma + '\t' + self.tokens[i].cpos + '\t' + self.tokens[i].pos + '\t' + self.tokens[i].feat + '\t' + str(self.tokens[i].head) + '\t' + self.tokens[i].deprel + '\t_\t_\n'
		return tmp

	def crossings(self, sent, align):
		return 0

	def edit_distance(self, sent):
		return ans

	def evaluate(self, gold):
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
			if not self.regex.match(token1.form) and token1.form not in self.etc:
				score[2] += 1
				if token1.head == token2.head:
					score[0] += 1
					if token1.deprel == token2.deprel:
						score[1] += 1
		return score

	def nonprojective_edges(self):
		ans = 0
		
		return ans

	def overlaps(self, sent, bigram=False, lower=False, punc=False):
		ans = 0
		words1 = self.words()
		words2 = sent.words()
		if bigram:
			tmp1 = ['START'] + words1 + ['END']
			tmp2 = ['START'] + words2 + ['END']
			words1, words2 = [], []
			for i in xrange(len(tmp1)-1):
				words1.append(tmp1[i] + '_' + tmp1[i+1])
			for i in xrange(len(tmp2)-1):
				words2.append(tmp2[i] + '_' + tmp2[i+1])
		if lower:
			words1 = [x.lower() for x in words1]
			words2 = [x.lower() for x in words2]
		dict1 = {}
		for word in words1:
			if punc and (self.regex.match(word) or word in self.etc):
				continue
			if word not in dict1:
				dict1[word] = 1
			else:
				dict1[word] += 1
		for word in words2:
			if punc and (self.regex.match(word) or word in self.etc):
				continue
			if word in dict1 and dict1[word] > 0:
				ans += 1
				dict1[word] -= 1
		return ans

	def words(self, no_root=True):
		return [x.form for x in self.tokens[1:]]

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
