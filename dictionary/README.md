## Steps to generate dictionary with word frequency

First I convert the 'original_dictionary.PDF' into 'dictionary.txt' where all
original information is preserved, only the file format is changed.

Next, I used 'parse_dict.py' to extarct all the useful words from 'dictionary.txt'
to form 'dict.txt' file, which contains only the plain words.

Finally, also in 'parse_dict.py', I generate a json file containing all the words
with its frequency (default to 500 for now) and add this json file into the
PySpellchecker instance so that we can use it in word correction.

I updated the 'misspelling_dict.py' file so that misspelling checker can load
my json file as a glossary.
