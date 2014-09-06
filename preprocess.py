import csv
import sys

def ascii(s):
	return all(ord(c) < 128 for c in s)

def check_unicode():
	if len(sys.argv) != 2:
		print 'usage: python preprocess.py paraphrases.csv'
		sys.exit(0)
	with open(sys.argv[1], 'rb') as csvfile:
		iter = 0
		reader = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in reader:
			if not ascii(row[2]):
				print iter, row[2]
			if not ascii(row[3]):
				print iter, row[3]

def fix_csv():
	if len(sys.argv) != 2:
		print 'usage: python preprocess.py paraphrases.csv'
		sys.exit(0)
	rows = []
	with open(sys.argv[1], 'rb') as csvfile:
		iter = 0
		reader = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in reader:
			iter += 1
			row[2] = remove_unicode(row[2])
			row[3] = remove_unicode(row[3])
			rows.append(row)
	write_to_file = False
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

# def read():
#     if len(sys.argv) != 2:
#         print 'usage: python preprocess.py parapharses.csv'
#         sys.exit(0)
#     f = open(sys.argv[1], 'r')
#     iter = 0
#     for line in f.read().splitlines():
#         iter += 1
#         words = line.split()
#         for word in words:
#             if not ascii(word):
#                 print iter, word
#         #print ' '.join(words)

# read()

def read_nbest(file):
	f = open(file, 'r')
	count = 0
	trees, pscores, rscores = [], [], []
	tmp, tmp2, tmp3 = [], [], []
	for line in f.read().splitlines():
		if count == 0:
			count = int(line)
			if tmp:
				trees.append(tmp)
				pscores.append(tmp2)
				rscores.append(tmp3)
				tmp, tmp2, tmp3 = [], [], []
			continue
		tokens = line.split('\t')
		if len(tokens) != 3:
			print 'Wrong Format'
			print line
			sys.exit(0)
		tmp.append(tokens[0])
		tmp2.append(float(tokens[1]))
		tmp3.append(float(tokens[2]))
		count -= 1
	return trees, pscores, rscores
		

def remove_unicode(s):
	s = s.replace('\xC2\x93', '``')
	s = s.replace('\xC2\x94', "''")
	s = s.replace('\xC2\x96', '--')
	s = s.replace('\xC3\xA2\xC2\x84\xC2\x87"', 'UNK')
	s = s.replace('\xC2\xBC', '1/4')
	s = s.replace('\xC2\xBD', '1/2')
	s = s.replace('\xC2\xBE', '3/4')
	return s

def main():
	#fix_csv()
	#check_unicode()
	trees, pscores, rscores = read_nbest(sys.argv[1])
	for ts, ps, rs in zip(trees, pscores, rscores):
		print len(ts), len(ps), len(rs)

main()
		
    
