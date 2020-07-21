#!/usr/bin/env python2.7

import unittest
from dnaseqlib import *

### Utility classes ###

# Maps integer keys to a set of arbitrary values.
class Multidict:
    # Initializes a new multi-value dictionary, and adds any key-value
    # 2-tuples in the iterable sequence pairs to the data structure.
    def __init__(self, pairs=[]):
        # raise Exception("Not implemented!")
        self.pairs = {}
        for key, value in pairs:
            if self.pairs.has_key(key):
                self.pairs[key].append(value)
            else:
                self.pairs[key] = [value]

    # Associates the value v with the key k.
    def put(self, k, v):
        # raise Exception("Not implemented!")
        subseq, pos = v[0][:], v[1]
        if self.pairs.has_key(k):
            self.pairs[k].append([subseq, pos])
        else:
            self.pairs[k] = [[subseq, pos]]

    # Gets any values that have been associated with the key k; or, if
    # none have been, returns an empty sequence.
    def get(self, k):
        # raise Exception("Not implemented!")
        if self.pairs.has_key(k):
            return self.pairs.get(k)
        else:
            return []

# Given a sequence of nucleotides, return all k-length subsequences
# and their hashes.  (What else do you need to know about each
# subsequence?)
def subsequenceHashes(seq, k):
    # print seq
    # raise Exception("Not implemented!")
    four_exp = [math.pow(4, i) for i in range(k)]
    base = pow(4, k)
    nuc_id = {'A':0, 'C':1, 'G':2, 'T':3, 'N':4}
    sub_seq = []
    hash_sub = 0
    # if len(seq) < k:
    #     raise ValueError("seq shorter than k")
    count = 0
    while True:
        try:
            i = next(seq)
        except StopIteration:
            break
        count += 1
        if count < k:
            hash_sub = hash_sub * 5 + nuc_id[i]
            sub_seq.append(i)
        else:
            hash_sub = hash_sub * 5 + nuc_id[i]
            hash_sub = hash_sub % base
            sub_seq.append(i)
            yield hash_sub, sub_seq, count - k + 1
            sub_seq.pop(0)
    # for i in range(k):
    #     hash_sub = hash_sub << 2 + nuc_id[seq[i]]
    #     sub_seq.append(seq[i])
    # i = k
    # yield hash_sub, sub_seq, 1
    # while i < len(seq):
    #     hash_sub = (hash_sub << 2 + nuc_id[seq[i]]) % base
    #     sub_seq.pop(0)
    #     sub_seq.append(seq[i])
    #     yield hash_sub, sub_seq, i - k + 1
    #     i = i + 1
    # yield None, None, None


# Similar to subsequenceHashes(), but returns one k-length subsequence
# every m nucleotides.  (This will be useful when you try to use two
# whole data files.)
def intervalSubsequenceHashes(seq, k, m):
    raise Exception("Not implemented!")

# Searches for commonalities between sequences a and b by comparing
# subsequences of length k.  The sequences a and b should be iterators
# that return nucleotides.  The table is built by computing one hash
# every m nucleotides (for m >= k).
def getExactSubmatches(a, b, k, m):
    # raise Exception("Not implemented!")
    aDict = Multidict()
    iterator = subsequenceHashes(a, k)
    while True:
        try:
            ahash, avalue, startpoint = next(iterator)
        except StopIteration:
            break
        # if ahash == None and avalue == None:
        #     break
        aDict.put(ahash, [avalue, startpoint])
    iterator = subsequenceHashes(b, k)
    resultlist = []
    while True:
        try:
            bhash, bvalue, bpoint = next(iterator)
        except StopIteration:
            break
        # if bhash == None and bvalue == None:
        #     break
        aget = aDict.get(bhash)
        if aget != []:
            for aval in aget:
                if aval[0] == bvalue:
                    resultlist.append([aval[1], bpoint])
    return resultlist



if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage: {0} [file_a.fa] [file_b.fa] [output.png]'.format(sys.argv[0])
        sys.exit(1)

    # The arguments are, in order: 1) Your getExactSubmatches
    # function, 2) the filename to which the image should be written,
    # 3) a tuple giving the width and height of the image, 4) the
    # filename of sequence A, 5) the filename of sequence B, 6) k, the
    # subsequence size, and 7) m, the sampling interval for sequence
    # A.
    compareSequences(getExactSubmatches, sys.argv[3], (500,500), sys.argv[1], sys.argv[2], 8, 100)
