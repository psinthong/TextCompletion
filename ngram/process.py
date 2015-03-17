import ngram
import re
import string
# from preprocess import *
from stemming.porter2 import stem
import nltk
import numpy as np
import math
def getNumChoices(allAns):
    line = 0
    for i in range(0,len(allAns)):
        number = len(allAns[i].strip())
        if number == 1:
            line += 5
        elif number == 2:
            line += 9
        elif number == 3:
            line += 27
        print line


if __name__ == "__main__":
    model = ngram.ngram(3)
    CountNumLine = 0
    qNum = 1
    # Train the model on text file preprocessed
    with open("preprocessed/train_set3.txt", 'r') as train_set:
        model.train(train_set.read())
    with open("questions_machine.txt", 'r') as questions_machine, \
    open("preprocessed/questions.txt", 'r') as questions_set, \
    open("answers_machine.txt", 'r') as ans_machine, \
    open("preprocessed/answers.txt", 'r') as answers_set:
        # prepare questions for preprocessing
        questions = questions_machine.read().split('\n')

        # format answers for easier comparison
        answers = ans_machine.read().split('\n')

        questions_set = questions_set.read().split('\n')
        answers_set = answers_set.read().split('\n')

        i = 0
        sentences = []
        words = ""
        rights = 0
        numBlanks = 0
        countLine = 0
        for line in questions:
            CountNumLine += 1 
            i += 1
            countLine += 1
            cnt = line.count('[')
            if cnt == 1:
                numBlanks = 5
            else:
                numBlanks = math.pow(3,cnt)
            if re.findall(r"\[(\w+)\]", line):
                # formating of the word to find
                word = re.findall(r"\[(\w+)\]", line) #--Stores all words in []
                line = questions_set[i - 1].split(' ')#--Read from preprocessed Qs
                # print "Line : ",line
                for w in range(0,len(word)):
                    eachWord = word[w]
                    eachWord = eachWord.translate(string.maketrans("",""), string.punctuation).lower()
                    eachWord = re.sub("[0-9]+", "7", eachWord)
                    eachWord = stem(eachWord)
                    word[w] = eachWord

                    # print eachWord
                    # Retrieve the words needed for ngram
                    
                    if eachWord in line:
                        pass
                    else:
                        for l in range(0,len(line)):
                            if(eachWord in line[l]):
                                line[l] = eachWord
                                break
                            else:
                                print "Line : ",line
                                print "Not in line : ",eachWord
                # print "Line : ",line
                if len(word) > 1:
                    sentences.append([])
                    for j in range(0,len(word)):
                        words=""
                        if line.index(word[j]) > 2:
                            words = ' '.join(line[line.index(word[j]) - 3 : line.index(word[j]) + 1])
                        else:
                            words = ' '.join(line[line.index(word[j]) - line.index(word[j]) : line.index(word[j]) + 1])
                        sentences[len(sentences)-1].append(words)
                        
                else:
                    if line.index(word[len(word)-1]) > 2:
                        words = ' '.join(line[line.index(word[len(word)-1]) - 3 : line.index(word[len(word)-1]) + 1])
                    else:
                        words = ' '.join(line[line.index(word[len(word)-1]) - line.index(word[len(word)-1]) : line.index(word[len(word)-1]) + 1])
                    sentences.append(words)
                words=""
                
                #--------------Comment out this section for Holmes Data---------------#
                if countLine == numBlanks:
                    countLine =0
                    tempAns =[]
                    # if re.search("\[(.*)\]", answers[qNum - 1]):
                    if re.findall(r"\[(\w+)\]", answers[qNum - 1]):
                        # ans_word = re.search("\[(.*)\]", answers[qNum - 1]).group(1)
                        ans_word = re.findall(r"\[(\w+)\]", answers[qNum - 1])
                        
                        for eachAns in ans_word:
                            eachAns = eachAns.translate(string.maketrans("",""), string.punctuation).lower()
                            eachAns = re.sub("[0-9]+", "7", eachAns)
                            eachAns = stem(eachAns)
                            tempAns.append(eachAns)
                    else: 
                        ans_word = ""

                    # Check success
                    print "**************************"
                    print "Compute prediction for question", qNum
                    # print "Sentences : ",sentences
                    # print "Weight : ",model.compute_prediction(sentences, 2)
                    result = sentences[np.argmax(model.compute_prediction(sentences, 2))]
                    # result = sentences[0]
                    qNum += 1
                    sentences = []
                    # print "Result before subtract : ",result
                    if len(result) < 4:
                        for k in range(0,len(result)):
                            result[k] = result[k].split(' ')[-1]
                    else:
                        result =[result.split(' ')[-1]]
                    print "Selected Ans: ",result 
                    print "Actual Ans: ",tempAns

                    if result == tempAns:
                        rights += 1   
                #--------------------------------------------------------------------#

                #---------------Comment out this section for GRE Data----------------#
                # if i%5 == 0:
                #     if re.search("\[(.*)\]", answers[i/5 - 1]):
                #         ans_word = re.search("\[(.*)\]", answers[i/5 - 1]).group(1)
                #         ans_word = ans_word.translate(string.maketrans("",""), string.punctuation).lower()
                #         ans_word = re.sub("[0-9]+", "7", ans_word)
                #         ans_word = stem(ans_word)
                #     else: 
                #         ans_word = ""

                #     # Check success
                #     print "Compute prediction for question", i/5
                #     result = sentences[np.argmax(model.compute_prediction(sentences, 2))]

                #     if result.split(' ')[-1] == ans_word:
                #         rights += 1
                #     sentences = []
                #--------------------------------------------------------------------#
        print len(answers), rights
        print "Success rate: ", (rights * 100.0) / (len(answers)) 