import gzip
import sys
from CoNLL import Corpus

# 0-index: 0 ROOT
def read_alignments(file):
	# 0: exact, 1: stem, 2: synonym, 3: paraphrase
	f = open(file, 'r')
	broken = []
	tmp = []
	count = 0
	for line in f.read().splitlines():
		if line == '':
			broken.append(tmp)
			tmp = []
			continue
		tmp.append(line)

	alignments = []
	for align in broken:
		alignment1 = []
		alignment2 = []		
		for line in align[4:]:
			tokens = line.split() # every score = 1.0. seems weird
			# ignore aligned phrases
			

def read_files(argv):
	sents = Corpus(argv[0]).sentences
	lines = gzip.open(argv[1]).read().splitlines()
	it = iter(sents)
	count = 0
	sd205, stats = [], []
	tmp1, tmp2 = [], []
	for line in lines:
		if count == 0:
			count = int(line)
			if tmp1:
				sd205.append(tmp1)
				stats.append(tmp2)
			continue
		tmp1.append(next(it))
		tokens = line.split('\t')
		if len(tokens) != 2:
			print 'Wrong Format'
			print line
			sys.exit(0)
		tmp2.append(float(tokens[1])) # only use reranker score
		count -= 1
	if tmp1:
		sd205.append(tmp1)
		stats.append(tmp2)
	return sd205, stats, read_alignments(argv[2])

def main():
	if len(sys.argv) != 4:
		print 'usage: python paraparse.py 50best.sd205, 50best.stats, align'
		sys.exit(0)
	trees, stats, align = read_files(sys.argv[1:])
	
main()
