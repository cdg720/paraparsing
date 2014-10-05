import gzip
import math
import sys
from CoNLL import Corpus

def add_scores(score1, score2): # natural log base
	#return score1 + score2 # mutiplication of scores given that scores are logs
	if score1 > score2:
		return score2 + math.log(1 + math.exp(score1 - score2))
	else:
		return score1 + math.log(1 + math.exp(score2 - score1))

def count_violations(tree1, tree2, align1, align2, label=False):
	count = 0
	for i in xrange(1, len(tree1)):
		if align1[i][0] == -1: # ith word not aligned
			continue
		head1 = tree1.tokens[i].head
		if align1[head1][0] == -1: # ith word's head not aligned
			continue
		twin = align1[i][0]
		head2 = tree2.tokens[twin].head
		if align2[head2][0] == -1: #
			#continue
			count += 1
		if align1[head1][0] != head2:
			count += 1
		elif tree1.tokens[i].deprel != tree2.tokens[twin].deprel:
			count += 0.5
			
	for i in xrange(1, len(tree2)):
		if align2[i][0] == -1:
			continue
		head2 = tree2.tokens[i].head
		if align2[head2][0] == -1:
			continue
		twin = align2[i][0]
		head1 = tree1.tokens[twin].head
		if align1[head1][0] == -1:
			#continue
			count += 1
		if align2[head2][0] != head1:
			count += 1
		elif tree2.tokens[i].deprel != tree1.tokens[twin].deprel:
			count += 0.5
	return count

def find_best_pair(trees1, trees2, align1, align2):
	args = [None, None]
	min_violation = 1000
	max_score = -1000
	for t1 in trees1:
		for t2 in trees2:
			c = count_violations(t1, t2, align1, align2, label=True) # doesn't care about labels
			score = add_scores(t1.score, t2.score)
			if c < min_violation:
				args = [t1, t2]
				min_violation = c
				max_score = score
			elif c == min_violation and score > max_score:
				args = [t1, t2]
				max_score = score
	return args

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
		len1 = len(align[1].split()) + 1
		len2 = len(align[2].split()) + 1
		align1 = [[-1,-1]] * len1
		align2 = [[-1,-1]] * len2
		for line in align[4:]:
			tokens = line.split() # every score = 1.0. seems weird and useless
			x = [int(tmp) for tmp in tokens[1].split(':')] # x -> y			
			y = [int(tmp) for tmp in tokens[0].split(':')] # y -> x
			# ignore aligned phrases (more than one word)
			if x[1] != 1 or y[1] != 1:
				continue
			align1[x[0]+1] = [y[0]+1, int(tokens[2])] # add one. ROOT is 0th word.
			align2[y[0]+1] = [x[0]+1, int(tokens[2])]
		alignments.append(align1)
		alignments.append(align2)
	return alignments

def read_files(argv):
	sents = Corpus(argv[0]).sentences
	lines = gzip.open(argv[1]).read().splitlines()
	it = iter(sents)
	count = 0
	sd205, tmp1 = [], []
	for line in lines:
		if count == 0:
			count = int(line)
			if tmp1:
				sd205.append(tmp1)
				tmp1 = []
			continue
		tmp1.append(next(it))
		tokens = line.split('\t')
		if len(tokens) != 2:
			print 'Wrong Format'
			print line
			sys.exit(0)
		tmp1[-1].score = float(tokens[1])
		count -= 1
	if tmp1:
		sd205.append(tmp1)
	align = read_alignments(argv[2])
	return sd205[::2], sd205[1::2], align[::2], align[1::2]

def main():
	if len(sys.argv) != 4:
		print 'usage: python paraparse.py 50best.sd205, 50best.stats, align'
		sys.exit(0)
	trees1, trees2, align1, align2 = read_files(sys.argv[1:])
	# output pairs that satisfy most contraints and have highest scores
	for ts1, ts2, a1, a2 in zip(trees1, trees2, align1, align2):
		best = find_best_pair(ts1, ts2, a1, a2)
		print best[0]
		print best[1]

	# output 1best parse
	# for ts1, ts2, a1, a2 in zip(trees1, trees2, align1, align2):
	# 	print ts1[0]
	# 	print ts2[0]

main()
