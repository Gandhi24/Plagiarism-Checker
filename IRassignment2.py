# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 19:44:28 2019

@author: Piyush Mishra
"""

import sys
import os.path
import os
import re
import random
import time
import binascii
from heapq import nlargest

documents = []
print ('Reading files')
print ('Please wait...')
t0 = time.time()

for file in os.listdir(r"C:\Users\Piyush Mishra\Desktop\Raw_Data"):

    filename = os.path.join(r"C:\Users\Piyush Mishra\Desktop\Raw_Data", file)
    f = open(filename, encoding = "latin-1")
    documents.append(f.read())

print ('Reading data took %.2f sec.' % (time.time() - t0))

print ('Total number of documents read is ' + str(len(documents)))

i = 0
docs_as_words_sets = {}

for document in documents:
    docs_as_words_sets[i] = re.sub("[^\w]", " ", document).split()
    i += 1
    

#print(docs_as_words_sets[0])
    
while True:
    shingle_size = input('Enter the shingle size:')
    try:
        shingle_size = int(shingle_size)
    except ValueError:
        print("Shingle size must be a positive integer....")
    if shingle_size > 0:
        break
    else:
        continue
    
docs_as_shingles_sets = {}

print("Shingling the documents....")

t0 = time.time()

totalShinglesCount = 0


#print(len(docs_as_words_sets))
for idx, words in docs_as_words_sets.items():  
    shingle = []
    #print(idx)
    #print(len(words))
    shinglesInDocWords = set()
    shinglesInDocInts = set()
    for i in range(len(words) - shingle_size + 1):
        shingle = words[i:i+shingle_size]
        shingle = ' '.join(shingle)
        #print(shingle)
        
        hashed_shingle = binascii.crc32(shingle.encode()) & 0xffffffff
         
        if shingle not in shinglesInDocWords:
            shinglesInDocWords.add(shingle)
            
        if hashed_shingle not in shinglesInDocInts:
            shinglesInDocInts.add(hashed_shingle)
            
            
    docs_as_shingles_sets[idx] = shinglesInDocInts
            
print ('Shingling Documents took %.2f sec.' % (time.time() - t0))       
    
#print(docs_as_words_sets[0])
#print(docs_as_shingles_sets[0])



total_shingle_set = set()
for idx, shingle_sets in docs_as_shingles_sets.items():
    #print(len(shingle_sets))
    for shingle in shingle_sets:
        if shingle not in total_shingle_set:
            total_shingle_set.add(shingle)


total_shingle_list = list(total_shingle_set)


#print(len(total_shingle_list))

   
numShingles = len(total_shingle_list)
numDocs = len(documents)
print ("Total number of shingles is: ",numShingles)
#print ("Total number of documents is: ", numDocs)

orig_matrix = [[0 for x in range(numDocs)] for y in range(numShingles)]
#print(len(orig_matrix))
#print(len(orig_matrix[0]))


for i in range(numShingles):
    for j in range(numDocs):
        if total_shingle_list[i] in docs_as_shingles_sets[j]:
            orig_matrix[i][j] = 1
            
   
         
t0 = time.time()

def createList(r1, r2): 
    return list(range(r1, r2+1)) 

def nextPermutation():
    temp = createList(0, numShingles)
    random.shuffle(temp)
    return temp

print ('\nGenerating permutations took %.2f sec.' % (time.time() - t0))     



while True:
    sigrows = input('Enter the number of Hash functions:')
    try:
        sigrows = int(sigrows)
    except ValueError:
        print("Number of hash functions must be a positive integer....")
    if sigrows > 0:
        break
    else:
        continue


def minhash(data):
	
    rows = len(data)
    cols = len(data[0])

    # initialize signature matrix with maxint
    sigmatrix = []
    for i in range(sigrows):
        sigmatrix.append([sys.maxsize] * cols)


    for i in range(sigrows):
        curPerm = nextPermutation()
        #print (curPerm)
        for col in range(cols):
            for row in range(rows):
                if data[row][col] == 0:
                    continue
                if sigmatrix[i][col] > curPerm[row]:
                    sigmatrix[i][col] = curPerm[row]

    return sigmatrix

#orig_matrix = [[0, 1, 0, 1], [1, 1, 0, 0], [1, 0, 0, 1], [1, 1, 1, 0]]
signature_matrix = minhash(orig_matrix)
#print(signature_matrix)

def JaccardSimilarityOrig(docID1, docID2):
    data = orig_matrix
    rows = len(data)
    a = 0
    b = 0
    for row in range(rows):
        if data[row][docID1]==1 and data[row][docID2]==1:
            a += 1
        elif data[row][docID1] == 1 or data[row][docID2] == 1:
            b += 1
    return (a/(a+b))

def JaccardSimilaritySig(docID1, docID2):
    data = signature_matrix
    rows = len(data)
    a = 0
    b = 0
    for row in range(rows):
        if data[row][docID1]==data[row][docID2] and data[row][docID1] < sigrows:
            a += 1
        elif data[row][docID1] <= sigrows or data[row][docID2] <= sigrows:
            b += 1
    return (a/(a+b))

while True:
    try:
        band_size = int(
            input("\nPlease enter the size of the band. Valid band sizes are 1 - " + str(sigrows) + ": "))
    except ValueError:
        print("Your input is not valid.")
        continue
    if band_size <= 0 or band_size > sigrows:
        print ("Your input is out of the defined range...")
        continue
    else:
        break



while True:
    try:
        testDocID = int(
            input("\nPlease enter the docID you want to query for. Valid IDs are 0 - " + str(numDocs-1) + ": "))
    except ValueError:
        print("Your input is not valid.")
        continue
    if testDocID < 0 or testDocID > numDocs:
        print ("Your input is out of the defined range...")
        continue
    else:
        break        

m = int(input("\nEnter the number of similar documents you want to retrieve: "))


print("\nSearching for ",m, " most similar documents in the corpus.....\n")   

#candidates = [i for i in range(numDocs)]
  


threshold = 0.2
def findCandidatesLSH(docID):
    i = docID
    candidates = []
    sim = [0 for n in range(numDocs)]
    for row in range(sigrows):
        if row % band_size == 0 :
                if row > 0 :
                    for col in range(numDocs):
                        if sim[col] >= threshold*band_size:
                            candidates.append(col)
                    sim = [0 for n in range(numDocs)]
        for col in range(numDocs):
            if signature_matrix[row][i] == signature_matrix[row][col]:
                sim[col] += 1
            
    return candidates     
            
            
                
                
candidates = findCandidatesLSH(testDocID)
#print(len(candidates))


CalcSimilarity = {}
TrueSimilarity = {}

def outputResults():
    for candidate in candidates:
        CalcSimilarity[candidate] = JaccardSimilaritySig(testDocID, candidate)
        TrueSimilarity[candidate] = JaccardSimilarityOrig(testDocID, candidate)
    
    mMostSimilar = nlargest(m, CalcSimilarity, key = CalcSimilarity.get) 
  
    print(m," most similar documents are:") 
    print("DocID: CalcSimilarity    TrueSimilarity") 
  
    for val in mMostSimilar: 
        print(val, "   : ", CalcSimilarity.get(val),"           ", TrueSimilarity.get(val)) 

    if len(mMostSimilar) < m:
        print("Rest of the documents are not sufficiently similar to the test Document")

#JSimOrig = JaccardSimilarityOrig(0, 9)
#JSimSig = JaccardSimilaritySig(0, 9)
#print (orig_matrix)
#print (JSimOrig)
#print (JSimSig)


outputResults()















































































































