from CoNLL import Corpus
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

import sys

def main():
	if len(sys.argv) != 4:
		print 'python run_classifier.py gold base dual'
		sys.exit(0)
	
