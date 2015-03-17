import numpy
import math
import scipy.sparse.linalg
import scipy.stats
#import pickle
import os
import sys
import itertools
import datetime
import re
from sklearn import preprocessing


class Lsa:
    def __init__(self):
        self.dictionary = {}
        
    def parse_documents(self, documents, count=False):
        """ Builds a dictionary of words encountered and in which sentences they are found """
        documents = [document.split(" ") for document in documents if len(document.split(" ")) > 1] # Minimum length of sentence
        self.number_documents = len(documents)
        self.total_words = 0
        for index,document in enumerate(documents):
            words = document
            for word in words:
                self.total_words += 1
                if count:
                    if word in self.dictionary:
                        self.dictionary[word] += 1
                    else:
                        self.dictionary[word] = 1
                else:
                    if word in self.dictionary:
                        self.dictionary[word].append(index)
                    else:
                        self.dictionary[word] = [index]
        if count:
            print self.total_words, "total words"
            self.total_words = float(self.total_words)
            print "Normalization"
            for word in self.dictionary.keys():
                self.dictionary[word] = self.dictionary[word]/self.total_words
        
    
    def build_count_matrix(self, common_threshold = 100): # common_threshold argument is useless for now
        """ Builds a matrix Words*Sentences from the dictionary """
        self.repeated_words = [word for word in self.dictionary.keys() if (len(self.dictionary[word])>5)]# and len(self.dictionary[word]) < self.number_documents*common_threshold)] # Min and max number of occurrences
        self.count_matrix = scipy.sparse.lil_matrix((len(self.repeated_words),self.number_documents))
        length = len(self.repeated_words)
        print "Started at", str(datetime.datetime.now())
        for index,word in enumerate(self.repeated_words):            
            pretty_counter(index,length)
            for document in self.dictionary[word]:
                self.count_matrix[index,document] += 1
        print
        print "Ended at", str(datetime.datetime.now())
        #self.count_matrix = self.count_matrix.tocsc()
    
    def train(self, documents):
        self.parse_documents(documents)
        print "Initial dictionary size:", len(self.dictionary.keys())
        self.build_count_matrix()
        print "Reduced dictionary size:", len(self.repeated_words)
        print "Number of sentences:", self.number_documents
        
    def weighting_tfidf(self):
        """ Term frequency/Inverse document frequency weighting
            Measures how common a term is across a sentence and how common it is across all documents """
        del self.dictionary # Memory management
        # Note: Could sum rows and columns on the fly to save memory
        column_sums = numpy.array(self.count_matrix.sum(axis=0))[0]
        #row_sums = numpy.sum(self.count_matrix > 0, axis=1)
        row_sums = numpy.array(self.count_matrix.astype("bool").astype("float32").sum(axis=1)).T[0]
        temp_matrix = self.count_matrix.tocoo()
        length = len(temp_matrix.data)
        print "Data entries to weight:", length
        number_documents_float = float(self.number_documents)
        counter = 0.0
        print "Started at", str(datetime.datetime.now())
        for row,column,value in itertools.izip(temp_matrix.row, temp_matrix.col, temp_matrix.data):
            tf = value/column_sums[column]
            idf = math.log(number_documents_float/row_sums[row])
            self.count_matrix[row,column] = tf*idf
            counter += 1.0
        print "Ended at", str(datetime.datetime.now())
    def reduce_dimensionality(self, trim = 250):
        """ Trims down matrices to only use a small number of important dimensions """
        print "Started at", str(datetime.datetime.now())
        self.words_u, self.singular_values, self.documents_vt = scipy.sparse.linalg.svds(self.count_matrix, trim)
        print "Ended at", str(datetime.datetime.now())
        #self.words_u, self.singular_values, self.documents_vt = scipy.linalg.svd(self.count_matrix)
        print self.words_u.shape, self.singular_values.shape
        del self.documents_vt # Memory management
        self.word_vectors = numpy.dot(self.words_u,numpy.diag(self.singular_values))


def pretty_counter(i,length):
    sys.stdout.flush()
    sys.stdout.write("\r"+str(round(float(i)/length,3))+"%")
        
def cosine_similarity(word1, word2):
    """ Returns a value between -1 (opposite semantic properties) and 1 (identical properties) """
    return numpy.dot(word1,word2)/(numpy.linalg.norm(word1)*numpy.linalg.norm(word2))


def gaussian_score(sentence, position, lsa, sigma):
	""" Scores a sentence with weighted similarities, a wide gaussian centered on the target word """
	score = 0
	finalScore = 0
	blankWords = re.findall(r"\[(\w+)\]", sentence)
	for word in blankWords:
            sentence = sentence.replace("\n","").replace(".","").replace(",","").replace("_","")
            words = sentence.split(" ")
            if word in lsa.repeated_words:
                target = lsa.repeated_words.index(word)
                target = lsa.word_vectors[target]
                pos = words.index("[" + word + "]")
                del(words[pos])
                gaussian = scipy.stats.norm(pos,sigma) 
                for i,wrd in enumerate(words):
                        weight = gaussian.pdf(i-pos)
                        if wrd in lsa.repeated_words:
                            score += weight*(cosine_similarity(target, lsa.word_vectors[lsa.repeated_words.index(wrd)]))
                score = score/(len(words)+1)
            finalScore = finalScore + score
     	return finalScore	 

def test_sentences(sentences, lsa, sigma, score = gaussian_score):
    """ Returns the scores for sentences, testing whether they are semantically compatible """
    position = 0
    positions = []
    for word1, word2 in zip(sentences[0].split(" ")[1:],sentences[1].split(" ")[1:]):
        if word1 == word2:
            position += 1
        else:
            break

    result = [score(sentence, position, lsa, sigma) for sentence in sentences]
    print "resulting weights: ", result
    print
    return numpy.argmax(result)

def test_whole(lsa, dataset, data = None, sigma = 4.5):
    sentences = []
    answers = []
    ansCount = 0
    fileNameQuestions = ""
    fileNameAnswers = ""
    answer_dictionary = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4}

    if dataset == "holmes":
        fileNameQuestions = "holmes_questions.txt"
        fileNameAnswers = "holmes_answers.txt"
    else:
        fileNameQuestions = "machine_questions.txt"
        fileNameAnswers = "machine_answers.txt"
       
    
    with open(fileNameQuestions) as openedfile:
        counter = 1
        question = []
        for line in openedfile:
            cnt = line.count('[')
            if cnt == 1:
                ansCount = 5
            else:
                ansCount = math.pow(3, cnt)
            if counter == ansCount:
                question.append(line)
                sentences.append(question)
                question = []
                counter = 1
            else:
                question.append(line)
                counter += 1
                
    sentences.append(question)
    print
    print len(sentences), " sets of questions to be tested"

    with open(fileNameAnswers) as openedfile:
        for line in openedfile:
            if dataset == "holmes":
                answer = line.split(" ")[0][-2]
                answers.append(answer_dictionary[answer])
            else:
                answers.append(line)
           
    print len(answers), " sets of answers to be tested"
    predictions = []
    for i,question in enumerate(sentences):
        pretty_counter(i,len(answers))
        print
        if len(question) != 0:
            predictions.append(test_sentences(question, lsa, sigma))
    performance = 0
    for i,prediction in enumerate(predictions):
        if dataset == "holmes":
            answer = prediction
        else:
            answer = sentences[i][prediction]
    print "Number of correctly guessed anwers:: ", performance, " Out of ", len(predictions)        
    print
    print "Performance score:: ", float(performance)/i*100, "%"
    return float(performance)/i*100

def read_files():
    filenames = os.listdir("training")
    sentences = []
    for filename in filenames:
        if filename[-4:].lower() == ".txt":
            with open(os.path.join("training",filename)) as openedfile:
                #print filename
                sentences.extend([line.replace("\n","") for line in openedfile])
    return sentences

def main():
    filenames = os.listdir("training")
    sentences = []
    print "Reading Files: "
    for filename in filenames:
        #print filename[-4:]
        if filename[-4:].lower() == ".txt":
            with open(os.path.join("training",filename)) as openedfile:
                print "filename", filename
                sentences.extend([line.replace("\n","") for line in openedfile])
    # LSA
    lsa = Lsa()
    print
    print "Parsing sentences: "
    lsa.train(sentences)
    print
    print "Starting Weighting Process:: "
    lsa.weighting_tfidf()
    print
    print "Starting SVD Decomposition Process::"
    lsa.reduce_dimensionality()
    numpy.save("word_vectors_new_250", lsa.word_vectors)
    numpy.save("word_table_new_250", lsa.repeated_words)
    #test_whole(lsa, "gre")
    test_whole(lsa, "holmes")
    return lsa
    
def loading():
    lsa = Lsa()
    lsa.count_matrix = numpy.load("pre_tfidf.sav.npy")
    lsa.weighting_tfidf()
    
if __name__ == "__main__":
    #loading()
    main()
