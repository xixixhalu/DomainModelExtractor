import nltk
import glob
import string
from spellchecker import SpellChecker
import re
import os

def word_count(file):
    # output word count on txt files without punctuation
    data = str()
    with open(file, "r") as myfile:
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
    with open(file, "r") as myfile:
        ret = myfile.read().lower().split('\n')
    return ret


def main():
    # DATA_DIR = "./Data/input_origin"
    # DATA_FILES = glob.glob(DATA_DIR + "/[0-9]*-USC-Project[0-9]*.txt")
    DATA_DIR = "./output/misspelling_detect_1"
    DATA_FILES = glob.iglob(DATA_DIR + "/[0-9]*-USC-Project[0-9]*corrected.txt")
    OUTPUT_DIR = "./Glossary/output/"
    spell = SpellChecker()

    # load glossary
    glossary = read_glossary("./Glossary/glossary.txt")
    spell.word_frequency.load_words(glossary)

    i=0
    j=0

    for file in DATA_FILES:
        wordCount = word_count(file)
        wordFreq = word_freq_count(wordCount, 1)
        j=j+len(wordFreq)
        misspelled = spell.unknown(wordFreq)
        res = list(misspelled)
        filename = os.path.basename(file)
        i=i+len(res)
        # write results
        with open (OUTPUT_DIR+filename+'output.txt','w') as f:
            for word in res:
                f.write('%s\n' % word)

    print("#words appears once: %d " % j)
    print("#words misspelled: %d " % i)



if __name__ == "__main__":
    main()
