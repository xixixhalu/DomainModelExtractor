import json
import pprint
import re
import os
import glob
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer, PorterStemmer

from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *

from util.file_op import fileOps


class Stemmer:
    def __init__(self, stemmer="porter"):
        self.__wnl = WordNetLemmatizer()
        if stemmer is "porter":
            self.__stemmer = PorterStemmer()
        if stemmer is "snowball":
            self.__stemmer = SnowballStemmer("english")


    def display(self, title, content):
        print '[' + title + ']'
        if title == 'Sentence':
            print content
            index = ''
            begin, end = 0, 0
            for elem in self.__output['sentences'][0]['tokens']:
                end = elem['characterOffsetEnd']
                for i in range(begin, end - len(str(elem['index']))):
                    index += ' '
                if re.match("^[,.]*$", elem['word']):
                    continue;
                index += str(elem['index'])
                begin = end
            print index
        elif type(content) is dict:
            print self.__printer.pprint(content)
        else:
	        print content


    def process_plural(self, sentence):
        d_flag = False

        self.__output = analyze(sentence)
        if self.__output is None:
            return None

        #td_result = TypeDep(self.__output)
        pt_result = parsePosTag(self.__output)

        #self.display('Sentence', sentence)
        #self.display('Type Dependency', td_result)
        #self.display('Pos-Tag', pt_result)

        origin = [x["word"] for x in self.__output['sentences'][0]['tokens']]
        
        if 'NNS' in pt_result:
            d_flag = True
            list_of_plurals = []
            for item in pt_result['NNS']:
                noun = self.__output['sentences'][0]['tokens'][item[0]-1 : item[1]]
                plural = ' '.join([d["word"] for d in noun])
                single = self.remove_s(plural, lower=True)

                single_words = single.split(' ')
                single_index = 0
                for i in range(item[0]-1, item[1]):
                    # print origin[i], single_words[single_index]
                    origin[i] = single_words[single_index]
                    single_index += 1

        if 'NNPS' in pt_result:
            d_flag = True
            list_of_plurals = []
            for item in pt_result['NNPS']:
                noun = self.__output['sentences'][0]['tokens'][item[0]-1 : item[1]]
                plural = ' '.join([d["word"] for d in noun])
                single = self.remove_s(plural, lower=True)

                single_words = single.split(' ')
                single_index = 0
                for i in range(item[0]-1, item[1]):
                    # print origin[i], single_words[single_index]
                    origin[i] = single_words[single_index]
                    single_index += 1

        result = ""
        for word in origin:
            if not re.match("^[0-9a-zA-Z_,.]*$", word):
                continue
            result += word + " "

        return result

    def remove_s(self, plural, lower=True):
        single = self.__wnl.lemmatize(plural) \
            if self.__wnl.lemmatize(plural).endswith('e') or self.__wnl.lemmatize(plural).endswith('y') \
            else self.__stemmer.stem(plural)

        single_word = single.split(' ')

        if lower is False:
            plural_word = plural.split(' ')

            plural_len = len(plural_word)
            single_len = len(single_word)
            for i in range(0, plural_len):
                if i >= single_len:
                    break
                p_w = list(plural_word[i])
                s_w = list(single_word[i])

                p_w_len = len(p_w)
                s_w_len = len(s_w)

                for j in range(0, p_w_len):
                    if j >= s_w_len:
                        break
                    if p_w[j] != s_w[j] and p_w[j].lower() == s_w[j]:
                        s_w[j] = p_w[j]
                r_w = ''.join(s_w)
                single_word[i] = r_w
            result = ' '.join(single_word)
            return result
        else:
            return single

	
if __name__ == '__main__':
    
    input_path = os.getcwd() + "/Data/input_origin/input/"
    output_path = os.getcwd() + "/Data/stemming/"

    sentence_size = 0
    execption_size = 0

    file_list = glob.glob(input_path + "*.txt") #2014-USC-Project01.txt

    print "Total size: " + str(len(file_list))

    stemmer = Stemmer("snowball")

    
    for file in file_list:
        result = []
        print "Proceessing" + file + "..."
        try:
            with open(file) as f:
                sentences = f.read().splitlines()
                for s in sentences:
                    result.append(stemmer.process_plural(s))
                    if not result is None:
                        sentence_size += 1
                    else:
                        execption_size += 1        
        except Exception as e:
            print "Error in " + file
            continue

        prefix, file_name = os.path.split(file)
        with fileOps.safe_open_w(output_path + file_name) as o:
            for r in result:
                o.write(r + '\n')

    print "total sentence size: " + str(sentence_size)
    print "total exception size: " + str(execption_size)
    
    
    # sentence = "As a user I can see advertisement from school and companies"
    # stemmer = Stemmer("porter")
    # print stemmer.process_plural(sentence)
    


