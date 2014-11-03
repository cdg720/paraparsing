import csv
import gzip
import sys
import time
from CoNLL import Corpus
from bllipparser import Tree

def ascii(s):
	return all(ord(c) < 128 for c in s)

def check_duplicate_tree(trees, cand):
	for tree in trees:
		if same(tree, cand):
			return True
	return False

def check_unicode():
	if len(sys.argv) != 2:
		print 'usage: python preprocess.py paraphrases.csv'
		sys.exit(0)
	with open(sys.argv[1], 'rb') as csvfile:
		ind = 0
		reader = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in reader:
			ind += 1
			if not ascii(row[2]):
				print ind, row[2], get_ord(row[2])
			if not ascii(row[3]):
				print ind, row[3], get_ord(row[3])

def fix_csv():
	if len(sys.argv) != 2:
		print 'usage: python preprocess.py paraphrases.csv'
		sys.exit(0)
	rows = []
	with open(sys.argv[1], 'rb') as csvfile:
		ind = 0
		reader = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in reader:
			ind += 1
			row[2] = remove_unicode(row[2])
			row[3] = remove_unicode(row[3])
			rows.append(row)
	write_to_file = True
	if write_to_file:
		f = open('fix.csv', 'w')
		for row in rows:
			f.write(row[0])
			f.write(',')
			f.write(row[1])
			f.write(',')
			if len(row[2]) > 0:
				f.write('"' + row[2] + '"')
			else:
				f.write(row[2])
			f.write(',')
			if len(row[3]) > 0:
				f.write('"' + row[3] + '"')
			else:
				f.write(row[3])
			f.write('\n')
		f.flush()
		f.close()

def get_ord(s):
	tmp = []
	for c in s:
		if ord(c) >= 128:
			tmp.append((c, ord(c)))
	return tmp

def get_words(input, out1, out2):
	f = open(input, 'r')
	g = open(out1, 'w')
	h = open(out2, 'w')
	ind = 0
	for line in f.read().splitlines():
		ind += 1
		if ind % 2 == 1:
			g.write(' '.join(Tree(line).tokens()) + '\n')
		else:
			h.write(' '.join(Tree(line).tokens()) + '\n')
	f.close()
	g.flush()
	g.close()
	h.flush()
	h.close()

def read_file(file):
	if file.endswith('.gz'):
		return gzip.open(file, 'rb')
	else:
		return open(file, 'r')

# TODO: fix this. very inefficient. make sure there is no bug
def remove_duplicates(trees, stats):
	corpus = Corpus(trees)
	f = read_file(stats)
	it = iter(corpus.sentences)
	count = 0
	g = gzip.open('50best.sd205.nodup.gz', 'wb')
	h = gzip.open('50best.stats.nodup.gz', 'wb')
	tmp1, tmp2, tmp3 = [], [], []
	for line in f.read().splitlines():
		if count == 0:
			count = int(line)
			if tmp1:
				tmp1, tmp2, tmp3 = trim(tmp1, tmp2, tmp3)
				h.write(str(len(tmp2)) + '\n')				
				for t1, t2, t3 in zip(tmp1, tmp2, tmp3):
					g.write(str(t1) + '\n')
					h.write(str(t2) + '\t' + str(t3) + '\n')
				tmp1, tmp2, tmp3 = [], [], []
			continue
		tokens = line.split('\t')
		if len(tokens) != 2:
			print 'Wrong Format'
			print line
			sys.exit(0)
		tmp1.append(next(it))
		tmp2.append(tokens[0])
		tmp3.append(tokens[1])
		count -= 1
	if tmp1:
		tmp1, tmp2, tmp3 = trim(tmp1, tmp2, tmp3)
		h.write(str(len(tmp2)) + '\n')				
		for t1, t2, t3 in zip(tmp1, tmp2, tmp3):
			g.write(str(t1) + '\n')
			h.write(str(t2) + '\t' + str(t3) + '\n')

def remove_unicode(s):
	s = s.replace('\xC2\x93', '``')
	s = s.replace('\xC2\x94', "''")
	s = s.replace('\xC2\x96', '--')
	s = s.replace('\xC3\xA2\xC2\x84\xC2\x87"', 'UNK')
	s = s.replace('\xC2\xBC', '1/4')
	s = s.replace('\xC2\xBD', '1/2')
	s = s.replace('\xC2\xBE', '3/4')
	s = s.replace('\x93', '``')
	s = s.replace('\x94', "''")
	s = s.replace('\x96', '--')
	s = s.replace('\xe2\x80\xa2', 'UNK')
	return s

def same(x, y):
	for token1, token2 in zip(x.tokens, y.tokens):
		if token1.head != token2.head:
			return False
		elif token1.head == token2.head and token1.deprel != token2.deprel:
			return False
	return True

def split_files(input, output, start, end):
	corpus = Corpus(input)
	f = open(output, 'w')
	for sent in corpus.sentences[2*(start-1):end*2]:
		f.write(str(sent) + '\n')
	f.flush()
	f.close()

def split_nbest_files(trees, stats, start, end):
	corpus = Corpus(trees)
	f = gzip.open(stats, 'rb')
	g = gzip.open('x', 'wb')
	h = gzip.open('y', 'wb')
	start = 2*(start-1) # 1-index
	end = 2*end
	it = iter(corpus.sentences)
	count = 0
	ind = 0
	for line in f.read().splitlines():
		if count == 0:
			count = int(line)
			ind += 1
			if ind >= start and ind <= end:
				h.write(str(count) + '\n')
			continue
		tree = next(it)
		tokens = line.split('\t')
		if len(tokens) != 2:
			print 'Wrong Format'
			print line
			sys.exit(0)
		if ind >= start and ind <= end:
			g.write(str(tree) + '\n')
			h.write(tokens[0] + '\t' + tokens[1] + '\n')
		count -= 1	

def trim(dtrees, pscores, rscores):
	x, y, z = [], [], []
	for dtree, ps, rs in zip(dtrees, pscores, rscores):
		if not check_duplicate_tree(x, dtree):
			x.append(dtree)
			y.append(ps)
			z.append(rs)
	return x, y, z

def main():
	#fix_csv() # get rid of unicode in .csv files
	check_unicode() # check if .csv file contains any unicode
	# remove_duplicates(sys.argv[1], sys.argv[2]) # remove duplicates in 50best.sd205
	# trees, pscores, rscores = read_nbest(sys.argv[1])
	# for ts, ps, rs in zip(trees, pscores, rscores):
	# 	print len(ts), len(ps), len(rs)
	# split_nbest_files(sys.argv[1], sys.argv[2], 1, 687) # get dev1/ data
	# split_files(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))

main()
