from CoNLL import Corpus, Sentence

from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC, NuSVC

from sklearn.cross_validation import LeaveOneOut, KFold

from collections import Counter

import csv
import numpy as np
import sys

import paraparse

def cross_validation(gold, base, dual, align):
	X, y, indices, _ = preprocess(gold, base, dual, align)
	if True:
		print >> sys.stderr, 'Leave One Out'
		kf = LeaveOneOut(len(y))
	else:
		print >> sys.stderr, '10-fold Cross Validation'
		kf = KFold(len(y), 10)
		
	correct = 0
	cl = get_classifier(which)
	out = []
	for train_indices, test_index in kf:
		# make sure train/test split is disjoint
		X_train, X_test = X[train_indices], X[test_index]
		y_train, y_test = y[train_indices], y[test_index]

		#cheating
		# X_train, X_test = X, X[test_index]
		# print >> sys.stderr, 'cheating!!'
		# y_train, y_test = y, y[test_index]
		try:
			cl.fit_transform(X_train, y_train)
		except:
			cl.fit(X_train, y_train)
		y_pred = cl.predict(X_test)
		out += list(y_pred)
		correct += sum([yp == yg for yp, yg in zip(y_pred, y_test)])
	evaluate(correct, indices, out, y, gold, base, dual)

def evaluate(correct, indices, out, y, gold, base, dual):
	count = 0
	gain, loss = 0, 0
	gains = [0,] * 10
	losses = [0,] * 10
	for ind in xrange(len(base)):
		if ind not in indices:
			if len(sys.argv) == 9:
				print base[ind][0]
				print base[ind][1]
		else: # base and dual parses have different scores
			val1 = base[ind][0].evaluate(gold[ind][0])
			val2 = dual[ind][0].evaluate(gold[ind][0])
			if out[count] == -1: # base parser
				if len(sys.argv) == 9:
					print base[ind][0]
					print base[ind][1]
			else: # dual parser
				if val1[0] > val2[0]:
					loss += val2[0] - val1[0]
					losses[val1[0] - val2[0] - 1] += 1
				else:
					gain += val2[0] - val1[0]
					gains[val2[0] -val1[0] - 1] += 1
				if len(sys.argv) == 9:				
					print dual[ind][0]
					print dual[ind][1]
			count += 1
	print >> sys.stderr, 'bin\t' + '\t'.join(str(x) for x in range(1,11))
	print >> sys.stderr, 'g ' + str(sum(gains)) + '\t' + '\t'.join(str(x) for x in gains)
	print >> sys.stderr, 'l ' + str(sum(losses)) + '\t' + '\t'.join(str(x) for x in losses)
	print >> sys.stderr, 'total gain: %d' % (gain + loss)
	print >> sys.stderr, 'classifier accuracy: %.2f (%d / %d)' % (100. * correct / len(y), correct, len(y))
	baseline = Counter(y)[-1]
	print >> sys.stderr, 'majority accuracy: %.2f (%d / %d)' % (100. * baseline / len(y), baseline, len(y))	

which = 1
def get_classifier(cl=0):
	if cl == 0:
		print >> sys.stderr, 'AdaBoostClassifier'
		#return AdaBoostClassifier()
		return AdaBoostClassifier(n_estimators=5, algorithm='SAMME', learning_rate=1)	
	elif cl == 1:
		print >> sys.stderr, 'LogisticRegression'
		return LogisticRegression(C=0.7)
		#return LogisticRegression(penalty='l1', C=0.8)
		#return LogisticRegression(penalty='l1', C=1)
		#return LogisticRegression(penalty='l1', C=2.9)
		#return LogisticRegression(penalty='l1', C=2.0) # lb, cpos: 58
	elif cl == 2:
		print >> sys.stderr, 'LinearSVC'
		#return LinearSVC(C=0.1)
		#return LinearSVC(penalty='l1', dual=False, C=1.5)
		#return LinearSVC(penalty='l1', dual=False, C=0.7) # lb: 60
		return LinearSVC(penalty='l1', dual=False, C=1.0)
		#return LinearSVC(loss='l1')
	# elif cl == 3:
	# 	return NuSVC(nu=0.4) # return some real number.
	else:
		print >> sys.stderr, 'invalid classifier'
		return None

# make sure the following method is correct
def get_features(base, dual):
	feats = {}
	for dp, sign in zip([base, dual], [-1, 1]):
		for i in xrange(1, len(dp)):
			pos = dp.tokens[i].pos
			cpos = pos[:2]
			lb = dp.tokens[i].deprel
			pos_lb = pos + ' ' + lb
			cpos_lb = cpos + ' ' + lb
			if dp.tokens[i].head != -1:
				p_lb = 'p' + dp.tokens[dp.tokens[i].head].deprel
			else:
				p_lb = 'pROOT'

			features = [lb, #v 18
									#lb + ' ' + p_lb, #v -15
									cpos, #x -9
									cpos_lb, #v -5
									pos, #x -4
									#pos_lb, #x 20
									]
			for feature in features:
				if feature in feats:
					#feats[feature] += sign
					if feats[feature] == sign * -1:
						 feats[feature] = 0
				else:
					feats[feature] = sign
	return feats

def get_features2(base, dual, align):
	feats = {}
	for i in xrange(1, len(base)):
		if align[0][i] == -1: # not aligned
			continue
		#if True:
		if base.tokens[i].head != dual.tokens[i].head:
			lb1 = base.tokens[i].deprel
			lb2 = dual.tokens[i].deprel
			cpos1 = base.tokens[i].cpos
			cpos2 = dual.tokens[i].cpos
			keys = [lb1 + ' ' + lb2,
							cpos1 + ' ' + cpos2,
							#'1 ' + lb1 + ' ' + cpos1,
							#'2 ' + lb2 + ' ' + cpos2,
							]
			for key in keys:
				if key in feats:
					feats[key] += 1
				else:
					feats[key] = 1
	return feats

def get_features3(sent1, sent2, align):
	x = []
	z = len(sent1.words())
	#z = 1
	# % of vocab overlaps
	x.append(float(Sentence.overlaps(sent1, sent2)) / z)
	#x.append(float(Sentence.overlaps(base, dual)))	
	# normalized edit_distance
	x.append(float(Sentence.edit_distance(sent1, sent2)) / z)
	#x.append(float(Sentence.edit_distance(base, dual)))	
	# normalized # of crossings
	x.append(float(Sentence.crossings(sent1, sent2, align[0], align[1])) / z)
	#x.append(float(Sentence.crossings(base, dual, align[0], align[1])))
	# length
	#x.append(z)
	return x

def preprocess(gold, base, dual, align):
	indices = []
	feat2ind = {}
	counts = {}
	X, y = [], []
	ind = 0
	src = source(sys.argv[7])
	for g, b, d, sauce in zip(gold, base, dual, src):
		b_score = b[0].evaluate(g[0])
		d_score = d[0].evaluate(g[0])
		# use LAS
		#if (b_score[0] > d_score[0] or (b_score[0] == d_score[0] and b_score[1] > d_score[1])):
		# use UAS
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
			# feats2 = get_features2(b[0], d[0], align[ind])
			# for f, v in feats2.iteritems():
			# 	if v != 0 and f not in feat2ind:
			# 		feat2ind[f] = len(feat2ind)
			# 	if v != 0:
			# 		if f in counts:
			# 			counts[f] += 1
			# 		else:
			# 			counts[f] = 1
			indices.append(ind)
		#elif b_score[0] < d_score[0] or (b_score[0] == d_score[0] and b_score[1] < d_score[1]):
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
			# feats2 = get_features2(b[0], d[0], align[ind])
			# for f, v in feats2.iteritems():
			# 	if v != 0 and f not in feat2ind:
			# 		feat2ind[f] = len(feat2ind)
			# 	if v != 0:
 			# 		if f in counts:
			# 			counts[f] += 1
			# 		else:
			# 			counts[f] = 1
			indices.append(ind)
		ind += 1
	th = 1
	for ind in indices:
		x = [0,] * (len(feat2ind) + 10)
		feats = get_features(base[ind][0], dual[ind][0])
		for f, v in feats.iteritems():
			if v != 0 and counts[f] > th:
				x[feat2ind[f]] = v
		# feats2 = get_features2(base[ind][0], dual[ind][0], align[ind])
		# for f, v in feats2.iteritems():
		# 	if v != 0 and counts[f] > th:
		# 		x[feat2ind[f]] = v
		vio1 = paraparse.count_violations(base[ind][0], base[ind][1], align[ind][0], align[ind][1])
		vio2 = paraparse.count_violations(dual[ind][0], dual[ind][1], align[ind][0], align[ind][1])
		sum_base_scores = paraparse.add_scores(base[ind][0].score, base[ind][1].score)
		sum_dual_scores = paraparse.add_scores(dual[ind][0].score, dual[ind][1].score)
		x[-1] = sum_base_scores
		x[-2] = sum_dual_scores
		# x[-3] = base[ind][0].score
		# x[-4] = dual[ind][0].score
		z = len(base[ind][0].words())
		#x[-9] = base[ind][1].score > dual[ind][1].score
		#x[-8] = sum_base_scores > sum_dual_scores
		#x[-7] = vio2 < vio1
		# x[-6] = float(Sentence.overlaps(base[ind][0], base[ind][1])) / z# overlaps
		# x[-5] = float(Sentence.edit_distance(base[ind][0], base[ind][1])) / z# edit distance
		# x[-4] = float(Sentence.crossings(base[ind][0], base[ind][1], align[ind][0], align[ind][1])) / z# crossings
		# x[-3] = base[ind][0].nonprojective_edges() - dual[ind][0].nonprojective_edges()
		# x[-2] = z < 20
		# x[-1] = len(base[ind][0].words()) < len(base[ind][1].words())
		X.append(x)
		
	print  >> sys.stderr, '# features:', len(feat2ind), '(before pruning)'
	print  >> sys.stderr, '# features:', sum([counts[x] > th for x in counts]), '(after pruning)'
	return np.array(X), np.array(y), indices, feat2ind

def preprocess2(gold, base, dual, align, feat2ind):
	indices = []
	X, y = [], []
	ind = 0
	for g, b, d in zip(gold, base, dual):
		b_score = b[0].evaluate(g[0])
		d_score = d[0].evaluate(g[0])
		# use UAS
		if (b_score[0] > d_score[0] or (b_score[0] == d_score[0] and b_score[1] > d_score[1])):
		#if b_score[0] > d_score[0]:
			y.append(-1)
			indices.append(ind)
		elif b_score[0] < d_score[0] or (b_score[0] == d_score[0] and b_score[1] < d_score[1]):
		#elif b_score[0] < d_score[0]:
			y.append(1)
			indices.append(ind)
		ind += 1
	for ind in indices:
		feats = get_features(base[ind][0], dual[ind][0])
		vio1 = paraparse.count_violations(base[ind][0], base[ind][1], align[ind][0], align[ind][1])
		vio2 = paraparse.count_violations(dual[ind][0], dual[ind][1], align[ind][0], align[ind][1])
		x = [0,] * (len(feat2ind) + 4)
		x[-1] = paraparse.add_scores(base[ind][0].score, base[ind][1].score)
		x[-2] = paraparse.add_scores(dual[ind][0].score, dual[ind][1].score)
		x[-3] = abs(x[-1] - x[-2]) / (len(base[ind][0]) + len(base[ind][0]))
		x[-4] = (vio1 - vio2) * 1. / (len(base[ind][0]) + len(base[ind][0]))		
		for f, v in feats.iteritems():
			if v != 0:
				x[feat2ind[f]] = v
		X.append(x)
	return np.array(X), np.array(y), indices

def preprocess3(gold, base, dual, align):
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
			#feats = get_features(b[0], d[0])
			feats = get_features2(b[0], d[0], align[ind])
			for f, v in feats.iteritems():
				if f not in feat2ind:
					feat2ind[f] = len(feat2ind)
				if f in counts:
					counts[f] += 1
				else:
					counts[f] = 1
			indices.append(ind)
		elif b_score[0] < d_score[0]:
			y.append(1)
			feats = get_features2(b[0], d[0], align[ind])
			for f, v in feats.iteritems():
				if f not in feat2ind:
					feat2ind[f] = len(feat2ind)
				if f in counts:
					counts[f] += 1
				else:
					counts[f] = 1
			indices.append(ind)
		ind += 1
	th = 1
	for ind in indices:
		feats = get_features2(base[ind][0], dual[ind][0], align[ind])
		vio1 = paraparse.count_violations(base[ind][0], base[ind][1], align[ind][0], align[ind][1])
		vio2 = paraparse.count_violations(dual[ind][0], dual[ind][1], align[ind][0], align[ind][1])
		x = [0,] * (len(feat2ind) + 7)
		x[-1] = paraparse.add_scores(base[ind][0].score, base[ind][1].score)
		x[-2] = paraparse.add_scores(dual[ind][0].score, dual[ind][1].score)
		x[-3] = abs(x[-1] - x[-2]) / (len(base[ind][0]) + len(base[ind][1]))
		x[-4] = (vio1 - vio2) * 1. / (len(base[ind][0]) + len(base[ind][1]))
		tmp = get_features3(base[ind][0], base[ind][1], align[ind])
		x[-5] = tmp[0]
		x[-6] = tmp[1]
		x[-7] = tmp[2]
		for f, v in feats.iteritems():
			if counts[f] > th:
				x[feat2ind[f]] = v
		X.append(x)

	print  >> sys.stderr, '# features:', len(feat2ind)
	print  >> sys.stderr, '# features:', sum([counts[x] > th for x in counts])
	return np.array(X), np.array(y), indices, feat2ind

def preprocess4(gold, base, dual, align):
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
			x = get_features3(b[0], b[1], align[ind])
			indices.append(ind)
		elif b_score[0] < d_score[0]:
			y.append(1)
			x = get_features3(b[0], b[1], align[ind])
			indices.append(ind)
		else:
			ind += 1
			continue
		X.append(x)
		ind += 1
	# print  >> sys.stderr, '# features:', len(feat2ind)
	# print  >> sys.stderr, '# features:', sum([counts[x] > th for x in counts])
	return np.array(X), np.array(y), indices, feat2ind

def read_data():
	tmp = Corpus(sys.argv[1]).sentences
	gold = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]
	tmp = Corpus(sys.argv[2]).sentences
	base = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]
	tmp = Corpus(sys.argv[3]).sentences
	dual = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]
	tmp = paraparse.read_alignments(sys.argv[4])
	align = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]

	tmp = open(sys.argv[5], 'r').read().splitlines()
	base_stats = [[float(x), float(y)] for x, y in zip(tmp[::2], tmp[1::2])]
	tmp = open(sys.argv[6], 'r').read().splitlines()	
	dual_stats = [[float(x), float(y)] for x, y in zip(tmp[::2], tmp[1::2])]
	for trees, stats in zip(base, base_stats):
		trees[0].score = stats[0]
		trees[1].score = stats[1]

	for trees, stats in zip(dual, dual_stats):
		trees[0].score = stats[0]
		trees[1].score = stats[1]
	return gold, base, dual, align

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
	X, y, _, feat2ind = preprocess(gold, base, dual, align)
	cl = get_classifier(which)
	try:
		cl.fit_transform(X, y)
	except:
		cl.fit(X, y)
	return cl, feat2ind

def test(cl, feat2ind, gold, base, dual, align):
	X, y, indices = preprocess2(gold, base, dual, align, feat2ind)
	y_pred = cl.predict(X)
	evaluate(sum(y_pred == y), indices, y_pred, y, gold, base, dual)

def main():
	if len(sys.argv) < 8:
		print 'python run_classifier.py gold base dual align base.stats dual.stats .csv (out)'
		sys.exit(0)
	gold, base, dual, align = read_data()
	# developing features with cross-validation
	cross_validation(gold, base, dual, align)

	# train and test
	# cl, feat2ind = train(gold, base, dual, align)
	# test(cl, feat2ind, gold, base, dual, align)

main()
