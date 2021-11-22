import nltk
import glob
import string
from spellchecker import SpellChecker
import re
import os
from pathlib import Path



def word_count(file):
    # output word count on txt files without punctuation
    with open(file, "r") as myfile:
        s = myfile.read().replace('\n', ' ').lower()
        del_str=string.punctuation
        replace_punctuation=' '*len(del_str)
        data=s.translate(str.maketrans(del_str,replace_punctuation))

    data = data.split(' ')
    fdist1 = nltk.FreqDist(data)
    return fdist1.most_common()


    #with open(file, "r") as file:
        #sentence_list=myfile.readlines()
        #for line in setence_list:
            #line=line.strip().lower()
            #del_str = string.punctuation
            #replace_punctuation = ' ' * len(del_str)
            #line=line.translate(str.maketrans(del_str,replace_punctuation))






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
    DATA_DIR = "./Data/input_origin"
    DATA_FILES = glob.iglob(DATA_DIR + "/[0-9]*-USC-Project[0-9]*.txt")
    #DATA_DIR = "./output/misspelling_detect_1"
    #ATA_FILES = glob.iglob(DATA_DIR + "/[0-9]*-USC-Project[0-9]*corrected.txt")
    OUTPUT_DIR = "./Glossary/output/"
    output_folder=Path(OUTPUT_DIR)
    if not output_folder:
        os.mkdir(OUTPUT_DIR)

    spell = SpellChecker()

    # load glossary
    glossary = read_glossary("./Glossary/glossary.txt")
    spell.word_frequency.load_words(glossary)
    spell.word_frequency.load_dictionary('./dictionary/dict.json')

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
        with open (OUTPUT_DIR+filename[:18]+'_corrected.txt','w') as f:
            for word in res:
                if len(word)>1:
                    f.write('%s\n' % word)

    print("#words appears once: %d " % j)
    print("#words misspelled: %d " % i)



if __name__ == "__main__":
    main()
