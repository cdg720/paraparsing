import sys

class Corpus:
	def __init__(self, file):
		self.read_file(file)

	def read_file(self, file):
		self.sentences = []
		f = open(file, 'r')
		tokens = []
		for line in f.read().splitlines():
			line = line.strip()
			if line == '':
				self.sentences.append(Sentence(tokens))
				tokens = []
				continue
			items = line.split('\t')
			if len(items) != 8:
				print 'Wrong Format'
				print line
				sys.exit(0)
			tokens.append(Token(items))
		if tokens: # not empty
			self.sentences.append(tokens)

class Sentence:
	def __init__(self, tokens):
		self.tokens = tokens

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
# 	corpus = Corpus('/home/dc65/Documents/data/tao/english08.test.lab')
# 	print len(corpus.sentences)
# 	print ' '.join([x.form for x in corpus.sentences[0].tokens])
# 	print ' '.join([x.form for x in corpus.sentences[-2].tokens])

# main()
