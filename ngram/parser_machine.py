# #!/bin/bash

# outf= open('./all_tests.txt')
# for f in ./tests/*.TXT; do
# 	cat $f >> ${outf}
# done
from  itertools import product
import re

question=""
answers=[]
# outputF = open("all_tests.txt","w+")
blankNum = 0

def writeToFile(filename, question, answers):
	with open(filename,"a+") as f:
		tempAns = question
		for r in product(*answers):
			for i in range(0,len(r)):
				tempAns = tempAns.replace('____','['+r[i]+']',1)
			# print tempAns
			f.write(tempAns+'\n')
			tempAns = question	
	f.close()
qNum = 0
with open("all_tests.txt") as f:
	for line in f:
		line = line.strip()
		# print line
		if "____" in line:
			qNum += 1
			blankNum = line.count("____")
			# print blankNum
			if len(question) > 0:
				# print answers,'\n'
				# print question,'\n'
				# tempAns = question
				# for r in product(*answers):
				# 	for i in range(0,len(r)):
				# 		tempAns = tempAns.replace('____',r[i],1)
				# 	print 'Ans: ',tempAns,'\n'
				# 	tempAns = question
				writeToFile('questions_machine.txt',question,answers)
				question = re.sub(r'\(.*?\)', '',line)
				answers=[]
				# // -----replace choices here and write to file----//
				# tempLine = line.replace("____",)
			# print question
			elif question == "":
				question = line
			if blankNum > 1:
				for i in range(0,blankNum):
					answers.append([])
			elif blankNum == 1:
				answers.append([])
		elif line !='' and ('Blank' not in line):
			if blankNum == 1:
				answers[0].append(line[3:])
			else:
				for i in range(0,blankNum):
					if len(answers[i]) < 3:
						answers[i].append(line[3:])
						break
		# print answers,'\n'
		# tempAns = question
		# for r in product(*answers):
		# 	for i in range(0,len(r)):
		# 		tempAns = tempAns.replace('____',r[i],1)
		# 	print 'Ans: ',tempAns,'\n'
		# 	tempAns = question
writeToFile('questions_machine.txt',question,answers)
# print answers,'\n'
# tempAns = question
# for r in product(*answers):
# 	for i in range(0,len(r)):
# 		tempAns = tempAns.replace('____',r[i],1)
# 	print 'Ans: ',tempAns,'\n'
# 	tempAns = question				

f.close()







# outputF.close()