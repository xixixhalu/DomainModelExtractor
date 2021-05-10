import nltk
import glob
import string
from spellchecker import SpellChecker
import re

def word_count(files):
	# output word count on txt files without punctuation 
	data = str()
	for file in files:
		with open (file, "r") as myfile:
			s = myfile.read().replace('\n', ' ').lower()
			data += s.translate(str.maketrans('', '', string.punctuation))
	data = data.split(' ')
	fdist1 = nltk.FreqDist(data)
	return fdist1.most_common()

def word_freq_count(wordCount, n):
	# output words with frequency n 
	ret = []
	for word, freq in wordCount:
		if freq == n:
			ret.append(word)
	return ret

def read_glossary(file):
	# output a list of strings in glossary file  
	with open (file, "r") as myfile:
			ret = myfile.read().lower().split('\n')
	return ret

def main():
    # DATA_DIR = "./Data/input_origin"
    # DATA_FILES = glob.glob(DATA_DIR + "/[0-9]*-USC-Project[0-9]*.txt")
    DATA_DIR = "./output/misspelling_detect_1"
    DATA_FILES = glob.glob(DATA_DIR + "/[0-9]*-USC-Project[0-9]*corrected.txt")

    wordCount = word_count(DATA_FILES)
    wordFreq = word_freq_count(wordCount, 1)
    print("#words appears once: %d " %len(wordFreq))
    spell = SpellChecker()
    
    # load glossary 
    glossary = read_glossary("./Glossary/glossary.txt")
    spell.word_frequency.load_words(glossary)

    misspelled = spell.unknown(wordFreq)
    print("#words misspelled: %d " %len(misspelled))
    res = list(misspelled)
    print(res)
    # write results 
    
    OUTPUT_DIR = "./Glossary/"
    with open(OUTPUT_DIR + "output.txt", "w") as f:
    	for word in res:
    		f.write('%s\n' % word)

if __name__ == "__main__":
    main()