from CoNLL import Corpus, Sentence

from sklearn.linear_model import LogisticRegression

from sklearn.cross_validation import LeaveOneOut, KFold

from collections import Counter

import csv
import numpy as np
import sys
import random

import paraparse

def cross_validation(gold, base, dual, align):
	X, y, indices, _, _2 = preprocess(gold, base, dual, align)
	if True:
		if not QUIET: print >> sys.stderr, 'Leave One Out'
		kf = LeaveOneOut(len(y))
	else:
		if not QUIET: print >> sys.stderr, '10-fold Cross Validation'
		kf = KFold(len(y), 10)

	correct = 0
	cl = get_classifier()
	out = []
	for train_indices, test_index in kf:
		# make sure train/test split is disjoint
		X_train, X_test = X[train_indices], X[test_index]
		y_train, y_test = y[train_indices], y[test_index]

		#cheating
		# X_train, X_test = X, X[test_index]
		# print >> sys.stderr, 'cheating!!'
		# y_train, y_test = y, y[test_index]
		cl.fit_transform(X_train, y_train)
		y_pred = cl.predict(X_test)
		out += list(y_pred)
		correct += sum([yp == yg for yp, yg in zip(y_pred, y_test)])
	return evaluate(correct, indices, out, y, gold, base, dual)

def evaluate(correct, indices, out, y, gold, base, dual):
	count = 0
	gain, loss = 0, 0
	gains = [0,] * 10
	losses = [0,] * 10
	for ind in xrange(len(base)):
		if ind not in indices:
			if len(sys.argv) == 6:
				print base[ind][0]
				print base[ind][1]
		else: # base and dual parses have different scores
			val1 = base[ind][0].evaluate(gold[ind][0])
			val2 = dual[ind][0].evaluate(gold[ind][0])
			if out[count] == -1: # base parser
				if len(sys.argv) == 6:
					print base[ind][0]
					print base[ind][1]
			else: # dual parser
				if val1[0] > val2[0]:
					loss += val2[0] - val1[0]
					losses[val1[0] - val2[0] - 1] += 1
				else:
					gain += val2[0] - val1[0]
					gains[val2[0] -val1[0] - 1] += 1
				if len(sys.argv) == 6:				
					print dual[ind][0]
					print dual[ind][1]
			count += 1
	if not QUIET:
		print >> sys.stderr, 'bin\t' + '\t'.join(str(x) for x in range(1,11))
		print >> sys.stderr, 'g ' + str(sum(gains)) + '\t' + '\t'.join(str(x) for x in gains)
		print >> sys.stderr, 'l ' + str(sum(losses)) + '\t' + '\t'.join(str(x) for x in losses)
		print >> sys.stderr, 'total gain: %d' % (gain + loss)
		print >> sys.stderr, 'classifier accuracy: %.2f (%d / %d)' % (100. * correct / len(y), correct, len(y))
		baseline = Counter(y)[-1]
		print >> sys.stderr, 'majority accuracy: %.2f (%d / %d)' % (100. * baseline / len(y), baseline, len(y))
	return 100. * correct / len(y)

def evaluate2(pred_y, base, dual):
	for p, b, d in zip(pred_y, base, dual):
		if p == -1:
			print b[0]
			print b[1]
		else:
			print d[0]
			print d[1]

def get_classifier():
	if not QUIET: print >> sys.stderr, 'LogisticRegression'
	#return LogisticRegression(C=1)

	return LogisticRegression(penalty='l1', C=1)
	#return LogisticRegression(penalty='l1', C=0.7)
	#return LogisticRegression(penalty='l1', C=2.9)
	#return LogisticRegression(penalty='l1', C=2.0) # lb, cpos: 58

# make sure the following method is correct
def get_features(base, dual):
	feats = {}
	for dp, sign in zip([base, dual], [-1, 1]):
		for i in xrange(1, len(dp)):
			pos = dp.tokens[i].pos
			cpos = pos[:2]
			lb = dp.tokens[i].deprel
			head = dp.tokens[i].head
			if head != -1:
				p_lb = dp.tokens[head].deprel
				p_pos = dp.tokens[head].pos
				p_cpos = p_pos[:2]
				p_head = dp.tokens[head].head
				if p_head != -1:
					gp_lb = dp.tokens[p_head].deprel
					gp_pos = dp.tokens[p_head].pos
					gp_cpos = gp_pos[:2]
				else:
					gp_lb = 'gpLB'
					gp_pos = 'gpPOS'
					gp_cpos = 'gpCPOS'
			else:
				p_lb = 'pLB'
				p_pos = 'pPOS'
				p_cpos = 'pCPOS'
				gp_lb = 'gpLB'
				gp_pos = 'gpPOS'
				gp_cpos = 'gpCPOS'

			features = []

			if sign == -1:
				prefix = 'b'
			else:
				prefix = 'd'
			if on[0] == '1': features.append(prefix + ' ' + lb)
			if on[1] == '1': features.append(prefix + ' ' + lb + ' ' + p_lb)
			if on[2] == '1': features.append(prefix + ' ' + lb + ' ' + gp_lb)
			if on[3] == '1': features.append(prefix + ' ' + lb + ' ' + p_lb + ' ' + gp_lb)
			if on[4] == '1': features.append(prefix + ' ' + cpos)
			if on[5] == '1': features.append(prefix + ' ' + cpos + ' ' + p_cpos)
			if on[6] == '1': features.append(prefix + ' ' + cpos + ' ' + p_cpos + ' ' + gp_cpos)
			if on[7] == '1': features.append(prefix + ' ' + cpos + ' ' + gp_cpos)
			if on[8] == '1': features.append(prefix + ' ' + cpos + ' ' + lb)
			if on[9] == '1': features.append(prefix + ' ' + cpos + ' ' + lb + ' ' + p_cpos)
			if on[10] == '1': features.append(prefix + ' ' + lb + ' ' + p_cpos + ' ' + p_lb)			

			for feature in features:
				feats[feature] = 1
			
	return feats

def preprocess(gold, base, dual, align):
	indices = []
	feat2ind = {}
	counts = {}
	X, y = [], []
	ind = 0
	for g, b, d in zip(gold, base, dual):
		b_score = b[0].evaluate(g[0])
		d_score = d[0].evaluate(g[0])
		if b_score[0] > d_score[0]:
			y.append(-1)
			feats = get_features(b[0], d[0])
			for f, v in feats.iteritems():
				if v != 0 and f not in feat2ind:
					feat2ind[f] = len(feat2ind)
				if v != 0:
					if f in counts:
						counts[f] += 1
					else:
						counts[f] = 1
			indices.append(ind)
		elif b_score[0] < d_score[0]:
			y.append(1)
			feats = get_features(b[0], d[0])
			for f, v in feats.iteritems():
				if v != 0 and f not in feat2ind:
					feat2ind[f] = len(feat2ind)
				if v != 0:
					if f in counts:
						counts[f] += 1
					else:
						counts[f] = 1
			indices.append(ind)
		ind += 1
	th = 2
	for ind in indices:
		x = [0,] * (len(feat2ind) + 10)
		feats = get_features(base[ind][0], dual[ind][0])
		for f, v in feats.iteritems():
			if v != 0 and counts[f] > th:
				x[feat2ind[f]] = v
		vio1 = paraparse.count_violations2(base[ind][0], base[ind][1], align[ind][0], align[ind][1])
		vio2 = paraparse.count_violations2(dual[ind][0], dual[ind][1], align[ind][0], align[ind][1])
		x[-1] = base[ind][0].nonprojective_edges() > dual[ind][0].nonprojective_edges()
		x[-2] = base[ind][1].nonprojective_edges() > dual[ind][1].nonprojective_edges()

		# sum_base_scores = paraparse.add_scores(base[ind][0].score, base[ind][1].score)
		# sum_dual_scores = paraparse.add_scores(dual[ind][0].score, dual[ind][1].score)

		# z = np.exp(sum_base_scores) + np.exp(sum_dual_scores)
		# x[-3] = np.exp(sum_base_scores) / z
		# x[-4] = np.exp(sum_dual_scores) / z
		# z = np.exp(base[ind][0].score) + np.exp(dual[ind][0].score)
		# x[-5] = np.exp(base[ind][0].score) / z
		# x[-6] = np.exp(dual[ind][0].score) / z
		# z = np.exp(base[ind][1].score) + np.exp(dual[ind][1].score)
		# x[-7] = np.exp(base[ind][1].score) / z
		# x[-8] = np.exp(dual[ind][1].score) / z
		# x[-9] = vio1 > vio2

		z = len(base[ind][0].words())
		if on[11] == '1': x[-3] = float(Sentence.edit_distance(base[ind][0], dual[ind][0])) / z
		if on[12] == '1': x[-4] = float(Sentence.crossings(base[ind][0], dual[ind][0], align[ind][0], align[ind][1])) / z
		if on[13] == '1': x[-5] = float(Sentence.overlaps(base[ind][0], dual[ind][0])) / z
		if on[14] == '1': x[-6] = len(base[ind][0].words()) >= len(base[ind][1].words())
		
		#x[-6] = vio1 > vio2
		#x[-7] = vio2 == 0
		X.append(x)

	if not QUIET:
		print  >> sys.stderr, '# features:', len(feat2ind), '(before pruning)'
		print  >> sys.stderr, '# features:', sum([counts[x] > th for x in counts]), '(after pruning)'
	return np.array(X), np.array(y), indices, feat2ind, counts

def preprocess2(base, dual, align, feat2ind, counts):
	X = []
	th = 2
	for b, d, a in zip(base, dual, align):
		x = [0,] * (len(feat2ind) + 10)
		feats = get_features(b[0], d[0])
		for f, v in feats.iteritems():
			if f in counts and counts[f] > th:
				x[feat2ind[f]] = v
		vio1 = paraparse.count_violations2(b[0], b[1], a[0], a[1])
		vio2 = paraparse.count_violations2(d[0], d[1], a[0], a[1])
		x[-1] = b[0].nonprojective_edges() > d[0].nonprojective_edges()
		x[-2] = b[1].nonprojective_edges() > d[1].nonprojective_edges()

		z = len(b[0].words())
		if on[11] == '1': x[-3] = float(Sentence.edit_distance(b[0], d[0])) / z
		if on[12] == '1': x[-4] = float(Sentence.crossings(b[0], d[0], a[0], a[1])) / z
		if on[13] == '1': x[-5] = float(Sentence.overlaps(b[0], d[0])) / z
		if on[14] == '1': x[-6] = len(b[0].words()) >= len(b[1].words())

		X.append(x)
	return np.array(X)

def read_data():
	tmp = Corpus(sys.argv[1]).sentences
	gold = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]
	tmp = Corpus(sys.argv[2]).sentences
	base = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]
	tmp = Corpus(sys.argv[3]).sentences
	dual = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]
	tmp = paraparse.read_alignments(sys.argv[4])
	align = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]

	# tmp = read_stats(sys.argv[5])
	# base_stats = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]
	# tmp = read_stats(sys.argv[6])
	# dual_stats = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]
	# for trees, stats in zip(base, base_stats):
	# 	trees[0].score = stats[0][0]
	# 	trees[1].score = stats[1][0]
	# 	trees[0].rank = stats[0][1]
	# 	trees[1].rank = stats[1][1]
	# 	trees[0].n = stats[0][2]
	# 	trees[1].n = stats[1][2]		
	# for trees, stats in zip(dual, dual_stats):
	# 	trees[0].score = stats[0][0]
	# 	trees[1].score = stats[1][0]
	# 	trees[0].rank = stats[0][1]
	# 	trees[1].rank = stats[1][1]
	# 	trees[0].n = stats[0][2]
	# 	trees[1].n = stats[1][2]		
	return gold, base, dual, align

def read_data2():
	tmp = Corpus(sys.argv[5]).sentences
	base = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]
	tmp = Corpus(sys.argv[6]).sentences
	dual = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]
	tmp = paraparse.read_alignments(sys.argv[7])
	align = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]
	return base, dual, align

def read_stats(file):
	tmp = open(file, 'r').read().splitlines()
	tmp = [t.split() for t in tmp]
	return [[float(t[0]), int(t[1]), int(t[2])] for t in tmp]

def source(file):
	src = []
	with open(file, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='"')
		ind = 0
		for row in reader:
			ind += 1
			if ind % 3 == 1:
				src.append(row[0])
	return src	

def train(gold, base, dual, align):
	X, y, _, feat2ind, counts = preprocess(gold, base, dual, align)
	cl = get_classifier()
	cl.fit_transform(X, y)
	return cl, feat2ind, counts

def test(cl, feat2ind, counts, base, dual, align):
	X = preprocess2(base, dual, align, feat2ind, counts)
	y_pred = cl.predict(X)
	evaluate2(y_pred, base, dual)

QUIET=False
size = 15
on = ['1'] * size
on = ['0', '1', '0', '0', '0', '0', '0', '1', '1', '0', '0', '0', '1', '0', '1'] # rbg 70.9
#on = ['1', '1', '1', '1', '0', '0', '0', '1', '0', '1', '1', '0', '1', '1', '0'] # self 73.7
#on = ['1', '0', '0', '1', '1', '1', '1', '0', '1', '1', '1', '0', '1', '0', '0'] # bllip 72.1
def main():
	development = True
	if development:
		if len(sys.argv) < 5:
			print 'python run_classifier.py gold.sd205 base.sd205 dual.sd205 align (out)'
			sys.exit(0)
		gold, base, dual, align = read_data()
		# developing features with cross-validation
		prev = cross_validation(gold, base, dual, align)
		#prev = 0

		if QUIET:
			while True:
				inds = [0] * random.randint(1,3)
				for i in xrange(len(inds)):
					inds[i] = random.randint(0,size-1)
					if on[inds[i]] == '1':
						on[inds[i]] = '0'
					else:
						on[inds[i]] = '1'

				val = cross_validation(gold, base, dual, align)
				if val >= prev:
					print prev, val
					prev = val
					print on
				else:
					if np.exp(val - prev) < random.random():
						for i in xrange(len(inds)):
							if on[inds[i]] == '1':
								on[inds[i]] = '0'
							else:
								on[inds[i]] = '1'
	else:
		if len(sys.argv) < 8:
			print 'python run_classifier.py train.gold train.base train.dual train.align test.base test.dual test.align'
			sys.exit(0)
		train_gold, train_base, train_dual, train_align = read_data()
		cl, feat2ind, counts = train(train_gold, train_base, train_dual, train_align)
		test_base, test_dual, test_align = read_data2()
		test(cl, feat2ind, counts, test_base, test_dual, test_align)

main()
