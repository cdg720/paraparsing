from CoNLL import Corpus

from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

from sklearn.cross_validation import LeaveOneOut

import numpy as np
import sys

def get_classifier(cl=0):
	if cl == 0:
		print >> sys.stderr, 'AdaBoostClassifier'
		return AdaBoostClassifier()
	elif cl == 1:
		print >> sys.stderr, 'LogisticRegression'
		#return LogisticRegression()
		return LogisticRegression(penalty='l1', C=1.0)	
	elif cl == 2:
		print >> sys.stderr, 'LinearSVC'
		return LinearSVC()
	else:
		print >> sys.stderr, 'invalid classifier'
		return None

def get_features(base, dual):
	feats = {}
	for i in xrange(1, len(base)):
		lb = base.tokens[i].deprel
		pos_lb = base.tokens[i].pos + ' ' + lb
		if lb in feats:
			if feats[lb] == 1:
				feats[lb] = 0
		else:
			feats[lb] = -1
		if pos_lb in feats:
			if feats[pos_lb] == 1:
				feats[pos_lb] = 0
		else:
			feats[pos_lb] = -1

	for i in xrange(1, len(dual)):
		lb = dual.tokens[i].deprel
		pos_lb = dual.tokens[i].pos + ' ' + lb
		if lb in feats:
			if feats[lb] == -1:
				feats[lb] = 0
		else:
			feats[lb] = 1
		if pos_lb in feats:
			if feats[pos_lb] == -1:
				feats[pos_lb] = 0
		else:
			feats[pos_lb] = 1
	return feats				

def preprocess(gold, base, dual):
	indices = []
	feat2ind = {}
	X, y = [], []
	ind = 0
	for g, b, d in zip(gold, base, dual):
		b_score = b[0].evaluate(g[0])
		d_score = d[0].evaluate(g[0])
		# use UAS
		if b_score[0] > d_score[0]:
			y.append(-1)
			feats = get_features(b[0], d[0])
			for f, v in feats.iteritems():
				if v != 0 and f not in feat2ind:
					feat2ind[f] = len(feat2ind)
			indices.append(ind)
		elif b_score[0] < d_score[0]:
			y.append(1)
			feats = get_features(b[0], d[0])
			for f, v in feats.iteritems():
				if v != 0 and f not in feat2ind:
					feat2ind[f] = len(feat2ind)
			indices.append(ind)
		ind += 1
	for ind in indices:
		feats = get_features(base[ind][0], dual[ind][0])
		x = [0,] * len(feat2ind)
		for f, v in feats.iteritems():
			if v != 0:
				x[feat2ind[f]] = v
		X.append(x)
	return np.array(X), np.array(y), indices

def main():
	if len(sys.argv) != 4:
		print 'python run_classifier.py gold base dual'
		sys.exit(0)
	tmp = Corpus(sys.argv[1]).sentences
	gold = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]
	tmp = Corpus(sys.argv[2]).sentences
	base = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]	
	tmp = Corpus(sys.argv[3]).sentences
	dual = [[x, y] for x, y in zip(tmp[::2], tmp[1::2])]

	X, y, indices = preprocess(gold, base, dual)
	loo = LeaveOneOut(len(y))
	correct = 0
	cl = get_classifier(1)
	out = []
	for train_indices, test_index in loo:
		X_train, X_test = X[train_indices], X[test_index]
		y_train, y_test = y[train_indices], y[test_index]
		try:
			cl.fit_transform(X_train, y_train)
		except:
			cl.fit(X_train, y_train)
		y_pred = cl.predict(X_test)
		out.append(y_pred[0])			
		if y_pred == y_test:
			correct += 1
	count = 0
	for ind in xrange(len(base)):
		if ind not in indices:
			print base[ind][0]
			print base[ind][1]
		else:
			if out[count] == -1:
				print base[ind][0]
				print base[ind][1]
			else:
				print dual[ind][0]
				print dual[ind][1]
			count += 1
	print >> sys.stderr, 'accuracy: %.2f' % (100. * correct / len(y))

main()
