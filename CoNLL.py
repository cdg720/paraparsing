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
			if len(items) != 10:
				print 'Wrong Format'
				print line
				sys.exit(0)
			tokens.append(Token(items))
		if tokens: # not empty
			self.sentences.append(tokens)

class Sentence:
	def __init__(self, tokens):
		self.tokens = tokens
		self.length = len(tokens)

	def __str__(self):
		tmp = ''
		for i in xrange(self.length):
			tmp += str(self.tokens[i].id) + '\t' + self.tokens[i].form + '\t' + self.tokens[i].lemma + '\t' + self.tokens[i].cpos + '\t' + self.tokens[i].pos + '\t' + self.tokens[i].feat + '\t' + str(self.tokens[i].head) + '\t' + self.tokens[i].deprel + '\n'
		return tmp

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
