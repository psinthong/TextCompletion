from  itertools import product
import re

question=""
blankNum = 0


def writeAnsToFile(filename, answer):
	f = open(filename,"a+")
	answer = answer.replace('.'," ").replace(','," ").replace('_'," ")
	# print answer
	f.write('<s> '+answer+' </s>\n')

ansFile = open('all_answers.txt')
answerSet = ansFile.readlines()
ansFile.close()
qNum = 0
with open("all_tests.txt") as f:
	for line in f:
		line = line.strip()
		# print line
		if "____" in line:
			qNum += 1
			blankNum = line.count("____")
			writeAnsToFile('answers.txt',question)
			question = re.sub(r'\(.*?\)', '',line)
		elif line !='' and ('Blank' not in line):
			if line[0:1] in answerSet[qNum-1]:
				# print line
				question = question.replace('____',line[3:],1)
writeAnsToFile('answers.txt',question)
f.close()







# outputF.close()