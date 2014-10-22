from CoNLL import Corpus

from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

from sklearn.cross_validation import LeaveOneOut

from collections import Counter

import numpy as np
import sys

def get_classifier(cl=0):
	if cl == 0:
		print >> sys.stderr, 'AdaBoostClassifier'
		#return AdaBoostClassifier()
		return AdaBoostClassifier(n_estimators=25, algorithm='SAMME', learning_rate=1.0)	
	elif cl == 1:
		print >> sys.stderr, 'LogisticRegression'
		#return LogisticRegression()
		#return LogisticRegression(penalty='l1', C=.6)
		#return LogisticRegression(penalty='l1', C=0.65)	# works best with dual3
		#return LogisticRegression(penalty='l1', C=1.5)
		return LogisticRegression(penalty='l1', C=2.0) # lb, cpos: 58
	elif cl == 2:
		print >> sys.stderr, 'LinearSVC'
		#return LinearSVC(penalty='l1', dual=False, C=0.15)
		return LinearSVC(penalty='l1', dual=False, C=0.7) # lb: 60
		#return LinearSVC(penalty='l1', dual=False, C=0.7)
		#return LinearSVC(loss='l1')	
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

			features = [lb,
									#lb + p_lb,
									#cpos,
									#cpos_lb,
									#pos,
									#pos_lb,
									]
			for feature in features:
				if feature in feats:
					if feats[feature] == sign * -1:
						feats[feature] = 0
				else:
					feats[feature] = sign
					
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
		#if b_score[0] > d_score[0] or (b_score[0] == d_score[0] and b_score[1] > d_score[1]):
		if b_score[0] > d_score[0]:
			y.append(-1)
			feats = get_features(b[0], d[0])
			for f, v in feats.iteritems():
				if v != 0 and f not in feat2ind:
					feat2ind[f] = len(feat2ind)
			indices.append(ind)
		#elif b_score[0] < d_score[0] or (b_score[0] == d_score[0] and b_score[1] < d_score[1]):
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
	if len(sys.argv) < 4:
		print 'python run_classifier.py gold base dual (out)'
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
	cl = get_classifier(2)
	out = []
	for train_indices, test_index in loo:
		# make sure train/test split is disjoint
		X_train, X_test = X[train_indices], X[test_index]
		y_train, y_test = y[train_indices], y[test_index]

		# cheating
		# X_train, X_test = X, X[test_index]
		# y_train, y_test = y, y[test_index]
		try:
			cl.fit_transform(X_train, y_train)
		except:
			cl.fit(X_train, y_train)
		y_pred = cl.predict(X_test)
		out.append(y_pred[0])			
		if y_pred == y_test:
			correct += 1

	count = 0
	gain, loss = 0, 0
	gains = [0,] * 10
	losses = [0,] * 10
	for ind in xrange(len(base)):
		if ind not in indices:
			if len(sys.argv) == 5:
				print base[ind][0]
				print base[ind][1]
		else: # base and dual parses have different scores
			val1 = base[ind][0].evaluate(gold[ind][0])
			val2 = dual[ind][0].evaluate(gold[ind][0])
			if out[count] == -1: # base parser
				if len(sys.argv) == 5:
					print base[ind][0]
					print base[ind][1]
			else: # dual parser
				if val1[0] > val2[0]:
					loss += val2[0] - val1[0]
					losses[val1[0] - val2[0] - 1] += 1
				else:
					gain += val2[0] - val1[0]
					gains[val2[0] -val1[0] - 1] += 1
				if len(sys.argv) == 5:				
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

main()
