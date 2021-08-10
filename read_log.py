import glob
import re
import os

def read_log(file):
    with open (file, 'r') as logfile:
        file_line=logfile.readlines()
        for line in file_line:
            if 'WARNING' in line:
                break
            else:
                print(line.strip())


DATA_DIR = "./output/misspelling_detect_1"
DATA_FILES = glob.iglob(DATA_DIR + "/[0-9]*-USC-Project[0-9]*log.txt")
for file in DATA_FILES:
    print(os.path.basename(file))
    read_log(file)

