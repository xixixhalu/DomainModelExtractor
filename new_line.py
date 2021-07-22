import glob
import os
DATA_DIR = "./output/misspelling_detect_1"
DATA_FILES = glob.glob(DATA_DIR + "/[0-9]*-USC-Project[0-9]*corrected.txt")
from pathlib import Path

newlines=[]

def auto_newline(file):
    with open(file, "r") as myfile:
        lines=myfile.readlines()
        for line in lines:
            word_list=line.split()
            for word in word_list:
                if '.' in word and word.count('.')==1 and word_list.index(word) != (len(word_list)-1) and word[-1]=='.':
                    word_list.insert(word_list.index(word)+1,'\n')
            output=' '.join(word_list)
            newlines.append(output)
    return newlines


OUTPUT_DIR = "./new_line/"
try:
    os.mkdir(OUTPUT_DIR)
except:
    pass


for file in DATA_FILES:
    res=auto_newline(file)
    filename = os.path.basename(file)
    with open (OUTPUT_DIR+filename[:18]+'_new_line.txt','w') as f:
        for line in res:
            f.write('%s\n' % line)