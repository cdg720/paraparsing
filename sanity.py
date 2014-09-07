import bllipparser
import sys

def check_tokenization(a, b):
	f = open(a, 'r')
	g = open(b, 'r')
	count = [0,] * 2
	for aa, bb in zip(f.read().splitlines(), g.read().splitlines()):
		tree1 = bllipparser.Tree(aa)
		tree2 = bllipparser.Tree(bb)
		if tree1.tokens() == tree2.tokens():
			count[0] += 1
		else:
			count[1] += 1
	print count

check_tokenization(sys.argv[1], sys.argv[2])
