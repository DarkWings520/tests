import os,sys,pdb,cv2,pickle
import numpy as np
import feat_lbp
from sklearn.svm import SVC

class CLF_SVM(object):
    def __init__(self, ft):
        self.fh = None
        self.clf = None
        self.clfpath = 'CLF_SVM_'+ft+'.dat'
        if 0 == cmp(ft, 'lbp'):
            self.fh = feat_lbp.FEAT_LBP()
        else:
            print 'unknown feature type'

    def get_samples(self, folderpath):
        if self.fh is None:
            print 'null feature handle'
            return (None,None)
        fvs, paths = self.fh.folder_mode(folderpath)
        fvs = np.array(fvs)
        return (fvs,paths)

    def predict(self, folderpath):
        if self.clf is None:
            with open(self.clfpath, 'rb') as f:
                self.clf = pickle.load(f)
        if self.clf is None:
            print 'clf is null'
            return
        tests,paths = self.get_samples(folderpath)
        print 'test ', tests.shape
        prds = self.clf.predict(tests)
        pos = ""
        neg = ""
        for prd, path in zip(prds, paths):
            if prd == 1:
                pos += path + '\n'
            else:
                neg += path + '\n'
        with open('pos.txt', 'w') as f:
            f.writelines(pos)
        with open('neg.txt', 'w') as f:
            f.writelines(neg)

        return

    def train(self, dataset):
        posinfo = self.get_samples(dataset + '/pos')
        print 'pos ', posinfo[0].shape
        neginfo = self.get_samples(dataset + '/neg')
        print 'neg ', neginfo[0].shape
        posnum = posinfo[0].shape[0]
        negnum = neginfo[0].shape[0]
        samples = np.vstack((posinfo[0], neginfo[0]))
        paths = posinfo[1].extend(neginfo[1])
        labels = [1 for k in range(posnum)] + [0 for k in range(negnum)]
        self.clf = SVC(C=1.0,kernel='linear',verbose=True).fit(samples, labels)
        prds = self.clf.predict(samples)
        TP = 0
        TN = 0
        for k in range(prds.shape[0]):
            if prds[k] == 1 and labels[k] == 1:
                TP += 1
            if prds[k] == 0 and labels[k] == 0:
                TN += 1
        print 'TP :', TP ,'/',posnum
        print 'TN :', TN ,'/',negnum
        with open(self.clfpath, 'wb') as f:
            pickle.dump(self.clf, f)
        return 

def do_train(dataset, ft):
    clf = CLF_SVM(ft)
    clf.train(dataset)

def do_test(folderpath, ft):
    clf = CLF_SVM(ft)
    clf.predict(folderpath) 

if __name__=="__main__":
    if len(sys.argv) == 3 and 0 == cmp(sys.argv[1],'-train'):
        ft = sys.argv[2]
        with open('config.txt', 'r') as f:
            dataset = f.readline().strip()
        do_train(dataset, ft)
    elif len(sys.argv) == 4 and 0 == cmp(sys.argv[1],'-test'):
        ft = sys.argv[2]
        folderpath = sys.argv[3]
        do_test(folderpath, ft)
    else:
        print 'unknown option'
