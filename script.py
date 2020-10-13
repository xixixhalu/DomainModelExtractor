import numpy as np
import re
from spellchecker import SpellChecker
import os

w = open('Data/inputOriginFix/dict.txt')
line = w.readline()
dicts = []
while line:
    dicts.append(line.strip())
    line = w.readline()
w.close()
print(dicts)
spell.word_frequency.load_words(dicts)


path = "Data/input_origin" #文件夹目录
files= os.listdir(path) #得到文件夹下的所有文件名称



def removeSlash(line):
    allresult = []
    slashLine = []
    slashLine.append(line)
    while len(slashLine)!=0:
        a = slashLine.pop()
        if "/" in a:
            wordlist = a.split(' ')
            i = 0 
            while "/" not in wordlist[i]:
                i+=1
            if "/" in wordlist[i]:
                b = wordlist[i].split("/")
                for j in b:
                    newLine = wordlist.copy()
                    newLine[i] = j           
                    slashLine.append(" ".join(newLine))
        else:
            allresult.append(a)
    return allresult

def wordCorrection(line):
    wordlist = line.split(" ")
    newList = wordlist.copy()
    
    for num,word in enumerate(wordlist):
        word = re.findall('[a-zA-z]+[\-\']?[a-zA-z]*',word)
        unknown = spell.unknown(word)
        if len(unknown)>0 and not word[0][0].isupper():
            print(unknown)
            correction = spell.correction(word[0])
            print(correction)
            candidate = newList[num]
            firstA = candidate.index(word[0])
            newWord = candidate[:firstA]+spell.correction(word[0])+candidate[firstA + len(candidate):]
            newList[num] = newWord
    return " ".join(newList)
 
    
# files = ["2014-USC-Project02.txt"]   
for file in files:
    print(file)
    f = open("Data/input_origin/"+file)
    w = open("Data/inputOriginFix/"+file,"w")
    line = f.readline()
    
    while line:
        line = re.sub(r'\(.*\)','',line).strip()
        if "/" in line:
            allresults = removeSlash(line)
            for i in allresults:
                w.write(wordCorrection(i))
                w.write("\n")
        else:
            w.write(wordCorrection(line))
            w.write("\n")

        line = f.readline()
    f.close()
    w.close()



            