import pandas as pd
from spellchecker import SpellChecker
import json

f = open('dictionary.txt', 'r')
cnt = 0
words = []
rep = {}
while True:
    line = f.readline()
    if not line:
        break
    line = line.strip()
    line = line.split()
    if len(line) > 2:
        if '(n)~' in line:
            idx = line.index('(n)~')
            word = line[:idx]
            #word = ' '.join(word)
            for w in word:
                if w in rep:
                    continue
                else:
                    rep[w] = True
                    words.append(w)
            #words.append(word)
        elif '(PN)~' in line:
            idx = line.index('(PN)~')
            word = line[:idx]
            #word = ' '.join(word)
            #words.append(word)
            for w in word:
                if w in rep:
                    continue
                else:
                    rep[w] = True
                    words.append(w)
        elif '(adj)~' in line:
            idx = line.index('(adj)~')
            word = line[:idx]
            #word = ' '.join(word)
            #words.append(word)
            for w in word:
                if w in rep:
                    continue
                else:
                    rep[w] = True
                    words.append(w)
        elif '(v)~' in line:
            idx = line.index('(v)~')
            word = line[:idx]
            #word = ' '.join(word)
            #words.append(word)
            for w in word:
                if w in rep:
                    continue
                else:
                    rep[w] = True
                    words.append(w)
        elif '(oth)~' in line:
            idx = line.index('(oth)~')
            word = line[:idx]
            #word = ' '.join(word)
            #words.append(word)
            for w in word:
                if w in rep:
                    continue
                else:
                    rep[w] = True
                    words.append(w)
        elif '~' in line:
            idx = line.index('~')
            word = line[:idx]
            #word = ' '.join(word)
            #words.append(word)
            for w in word:
                if w in rep:
                    continue
                else:
                    rep[w] = True
                    words.append(w)
        else:
            continue

res_dict = {}
for i in words:
    res_dict[i] = 500

words_json = json.dumps(res_dict)

with open('dict.json', 'w') as outfile:
    json.dump(res_dict, outfile)

with open('dict.txt', 'w') as outfile:
    for i in words:
        outfile.write(i + '\n')
outfile.close()

spell = SpellChecker(case_sensitive=True)

spell.word_frequency.load_dictionary('dict.json')
