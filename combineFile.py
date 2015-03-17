
# ansFile = open('all_answers.txt')
# answerSet = ansFile.readlines()
# ansFile.close()
toWriteFile = open('all_answers.txt','a+')
for i in range(0,10):
	filename = 'answers/answerSet'+str(i+1)+'.txt'
	f = open(filename)
	# temp = f.readlines()
	toWriteFile.write(f.read())
	f.close()
	toWriteFile.write('\n')
toWriteFile.close()