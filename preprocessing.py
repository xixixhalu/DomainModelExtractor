import os
import re

from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *

from util.logger import Logger
global logger

from util.Map import Map

import itertools
import collections

import argparse


# create a class to pre-process
# 0. Remove brackets, remove slashes
# 1. replace I with role
# 2. combine consecutive Nouns
# 3. output another identical file

FUNC_RE = '(A|a)s (the|a|an) .+(I|i|My|my) '
LEMMA_STOP_WORDS = {'data'}


class PreProcessor:

    def __init__(self):
        self.count_func = 0
        self.count_nonfunc = 0

    def pre_process(self, input_path, output_path):

        CONNECTOR = '!#%'
        # Connector used for RemoveSlash
        file = open(input_path, 'r')

        func_output = open(output_path + ".func.txt", "w")
        nonfunc_output = open(output_path + ".nonfunc.txt", "w")
        metadata = open(output_path + ".meta.txt", "w")
        actors = open(output_path + ".actor.txt", "w")

        line = file.readline().strip()
        while line:
            # print("Original sentence: ", line)
            if re.search(FUNC_RE, line):
                meta = []

                # maps combined noun to the original nouns
                noun_map = {}
                acts = []
                try:
                    line_no_bracket = self.removeBracket(line)
                except:
                    logger.error("removeBracket: Cannot process sentence > " + line)
                    line_no_bracket = line
                # try:
                line_no_slash = self.removeSlash(line_no_bracket,CONNECTOR=CONNECTOR)
                print(line_no_slash)
                for i in line_no_slash:
                    combine_nouns_line = self.combine_nouns(i, meta, noun_map)
                    replace_role_line = self.replace_role(combine_nouns_line, noun_map, acts)                        
                    func_output.write(replace_role_line + "\n")
                    self.count_func += 1   
                        # After processing using "RemoveSlash", line_no_slash will become a list.
                        # Loop in the list so that every function will be wriiten into the file.

                # except:
                #     logger.error("removeSlash: Cannot process sentence > " + line)
                    
                #     combine_nouns_line = self.combine_nouns(line_no_bracket, meta, noun_map)
                #     replace_role_line = self.replace_role(combine_nouns_line, noun_map, acts)
                #     func_output.write(replace_role_line + "\n")
                #     self.count_func += 1
            else:
                nonfunc_output.write(replace_role_line + "\n")
                self.count_nonfunc += 1
            metadata.write(meta.__str__() + "\n")
            actors.write(acts.__str__() + "\n")

                # print("Meta data: ", meta)
                # print(" ")

            line = file.readline().strip()



        logger.info("Functional count: " + str(self.count_func) + 
                    "\nNon-functional count: " + str(self.count_nonfunc))

        func_output.close()
        nonfunc_output.close()
        metadata.close()
        actors.close()

        file.close()

    # Note: this function check if a word is in stop words dict, if no, return lemma form, otherwise, return original word.
    def filter_stop_word(self, idx, nlp_output):
        tokens = nlp_output['sentences'][0]['tokens']
        word = tokens[idx]['originalText']
        is_stop_word = False
        for w in LEMMA_STOP_WORDS:
            if word.lower() == w: #or w.endswith(word.lower()):
                is_stop_word = True
                break
        if not is_stop_word:
            word = tokens[idx]['lemma']
        return word

    # Note: this function use a straight forward method to combine consecutive nouns: combining consecutive NN or NNP or
    # NNS or NNPS.
    def combine_nouns(self, line, meta, noun_map):
        nlp_output = analyze(line)
        if nlp_output is None:
            # print(line, ": NLP API returns None. skip!")
            return ''
        # print(json.dumps(nlp_output, indent=2))

        line_index = []
        # print(nlp_output)
        for i in range(0, len(nlp_output['sentences'][0]['tokens']) + 1):
            line_index.append(i)
        # print("According index:", line_index)

        pt = parsePosTag(nlp_output)
        # print("POS Tags: ", pt)
        td_key = pure_enhancedTD(nlp_output)
        # print("Type Dependencies: ", td_key)
        tokens = nlp_output['sentences'][0]['tokens']

        # Note: if you want to combine other words, please add them as a list of intervals so that the function
        # 'merge_intervals' can process it.
        intervals = []
        intervals.extend(self.combine_JJs_NNs(line_index, pt))
        # Bo: no need to combine nmod
        # intervals.extend(self.combine_nmod(td_key))
        intervals = self.merge_intervals(intervals)
        

        intervals = self._check_intervals(intervals, tokens)

        map = {}
        for pair in intervals:
            map[pair[0]] = pair[1]

        new_line = ''
        i = 1

        # construct combined sentence
        while i < len(line_index):
            cand = tokens[i - 1]['word']

            if i in map:
                cand = self.filter_stop_word(i-1, nlp_output)
                cand = cand[0].upper() + cand[1:]
                j = map[i]
                i = i + 1
                while i <= j:
                    cand += self.filter_stop_word(i-1, nlp_output)[0].upper() + self.filter_stop_word(i-1, nlp_output)[1:]
                    i = i + 1

                i = i - 1
                # cand = re.sub(r'\W+', '', cand)

            if cand == ',' or cand == '.':
                new_line = new_line.strip()
            new_line += cand
            if cand != '`':
                new_line += ' '

            i = i + 1

        new_line = new_line.strip()

        # construct meta data
        for pair in intervals:
            combined = ''
            sub = []
            i = pair[0]
            while i <= pair[1]:
                sub.append(self.filter_stop_word(i-1, nlp_output))
                combined += self.filter_stop_word(i-1, nlp_output)[0].upper() + self.filter_stop_word(i-1, nlp_output)[1:]
                i = i + 1
            # combined = re.sub(r'\W+', '', combined)
            noun_map[combined] = sub
            meta.append((sub, pair))

        # print("Combined sentence: ", new_line)
        # print("Combined nouns mapping: ", noun_map)

        return str(new_line)

    # Take a list of intervals and return a list of non-overlapped intervals
    def merge_intervals(self, intervals):
        if len(intervals) <= 1:
            # print("skip merging intervals.")
            return intervals

        intervals.sort(key=lambda tup: (tup[0], tup[1]))
        # print("sorted intervals: ", intervals)

        list = []
        curr = intervals[0]
        i = 1

        while i < len(intervals):
            next = intervals[i]
            while curr[1] >= next[0]:
                tail = max(curr[1], next[1])
                curr = (curr[0], tail)
                i = i + 1
                if i < len(intervals):
                    next = intervals[i]
                else:
                    next = None
                    break
            list.append(curr)
            curr = next
            i = i + 1

        if curr is not None:
            list.append(curr)

        # print("merged intervals: ", list)

        return list

    # Return a list of index intervals that we should combine
    def combine_nmod(self, td_key):
        list = []
        if 'nmod:of' in td_key:
            for pair in td_key['nmod:of']:
                p1 = min(pair[0], pair[1])
                p2 = max(pair[0], pair[1])
                list.append((p1, p2))

        return list

    def _check_intervals(self, intervals, tokens):
        '''
        This function is responsible for filtering invalidate intervals to assist future steps.
        All invalidate words are included in key_words and key_phrase_words.
        Please note that this function exploit lemmatization from Stanford NLP API, so users do not need to care about
        words' inflection.
        1. If an interval contains a word in key_words called key, this function will use all the words except key_word
        to construct new intervals.
        2. If an interval contains a word in key_phrase_words and and its next word is "of", this function will also
        remove them as well as construct new intervals.


        eg.
        Input: Include UCS Validate PIN.
        Original output:IncludeUCSValidatePIN.
        Current output: Include UCSValidatePIN.
        ----------------------------------------
        Input: Cardreader , Cashdispenser and Receiptprinter are parts of the schedule of ATM.
        Original output: Cardreader, Cashdispenser and Receiptprinter are PartsOfTheScheduleOfATM.
        Current output: Cardreader , Cashdispenser and Receiptprinter are parts of the ScheduleOfATM.
        :param intervals:
        :param tokens:
        :return: _intervals
        '''

        _intervals = []
        key_words = ["include", "extend", "resume", "repeat", "contain", "an", "a"]
        key_phrase_words = ["part", "unit", "member", "consist", "make", "compose", "kind", "type", "parent"]

        def combine_tokens(interval, tokens):
            res = []
            for i in range(interval[0], interval[1] + 1):
                token = tokens[i-1]["lemma"].lower()
                res.append(token)
            return res
        for interval in intervals:
            candidates = combine_tokens(interval, tokens)
            start = interval[0]
            end = interval[1]
            _start = start
            i = 0
            while i < len(candidates):
                word = candidates[i]
                if word in key_words:
                    if start + i - 1 >= _start:
                        _intervals.append((_start, start + i - 1))
                    _start = start + i + 1
                elif word in key_phrase_words:
                    if i + 1 < len(candidates) and candidates[i+1] == "of":
                        if start + i - 1 >= _start:
                            _intervals.append((_start, start + i - 1))
                    _start = start + i + 2
                    i += 1
                i += 1
            if _start <= end:
                _intervals.append((_start, end))

        return _intervals

    # Return a list of index intervals that we should combine
    def combine_JJs_NNs(self, line_index, pt):
        # Add all NN or NNP or NNS or NNPS to a set
        nouns = set()
        # dashes = set()

        # if 'HYPH' in pt:
        #     for pair in pt['HYPH']:
        #         if tokens[pair[0] - 1]['originalText'] == '-':
        #             dashes.add(pair[0])
        if 'NN' in pt:
            for pair in pt['NN']:
                nouns.add(pair[0])
        if 'NNS' in pt:
            for pair in pt['NNS']:
                nouns.add(pair[0])
        if 'NNP' in pt:
            for pair in pt['NNP']:
                nouns.add(pair[0])
        if 'NNPS' in pt:
            for pair in pt['NNPS']:
                nouns.add(pair[0])

        # Add all JJ to a set
        adjs = set()
        # Bo: no need to consider JJ
        # if 'JJ' in pt:
        #     for pair in pt['JJ']:
        #         adjs.add(pair[0])

        list = []
        i = 1
        while i < len(line_index):
            if i in adjs:
                flag = False
                j = i + 1
                # if only consecutive JJs, we should not combine them, so we should judge if there is at least one NN
                # after JJs
                while j < len(line_index) and (j in adjs or j in nouns):
                    if j in nouns:
                        flag = True
                        break
                    j = j + 1

                # if flag is True, it means that the pattern is JJ + JJ + JJ + .... + NN, and it is likely that there
                # are other consecutive NN after the first NN, e.g. JJ JJ NN, JJ JJ NN NN. We only store the interval
                # (index of the first JJ, index of the first NN), e.g. JJ1 JJ2 NN1 NN2 -> (JJ1, NN1), not (JJ1, NN2),
                # and the final output of this function will be (JJ1, NN1) + (NN1, NN2).
                if flag:
                    list.append((i, j))

                i = j

            elif i in nouns:
                # we only store consecutive NNs
                # Note: we do not care the case where a JJ is between two consecutive NNs, e.g. NN JJ NN.
                j = i + 1
                while j < len(line_index) and j in nouns:
                    j = j + 1

                # if j > i + 1:
                list.append((i, j - 1))

                i = j

            else:
                i = i + 1

        # print("JJ + NN: ", list)
        return list

    def replace_role(self, line, noun_map, act):
        nlp_output = analyze(line)
        noun_set = {'NN', 'NNP', 'NNS', 'NNPS'}
        tokens = [d['word'] for d in nlp_output['sentences'][0]['tokens']]
        pos_tags = [d['pos'] for d in nlp_output['sentences'][0]['tokens']]
        outputs = []

        repalce_occured = False
        for i in range(len(tokens)):
            if tokens[i] == 'As' or tokens[i] == 'as':
                # "As a xxx" pattern
                if tokens[i + 1] == 'a' or tokens[i + 1] == 'an':
                    idx = i + 2
                # "As xxx" pattern should only consider when it is the start of the sentence
                elif i == 0:
                    idx = i + 1
                else:
                    continue

                outputs.extend(tokens[:i])

                while idx < len(pos_tags) and pos_tags[idx] not in noun_set:
                    idx += 1

                role = tokens[idx]
                outputs.extend(tokens[idx + 1:])

                if outputs[i] == ',':
                    outputs.pop(i)

                def index(tokens, original, replace):
                    isReplaced = False
                    for i, token in enumerate(tokens):
                        if token == original:
                            tokens[i] = replace
                            isReplaced = True
                    return isReplaced

                self.extract_actors(role, noun_map, act)
                subjects = ['I', 'i', 'we', 'We']
                for subject in subjects:
                    repalce_occured = index(outputs, subject, role) or repalce_occured
                pronouns = ['my', 'My']
                for pronoun in pronouns:
                    repalce_occured = index(outputs, pronoun, role + "'s") or repalce_occured
                
                break
                
        if not repalce_occured:
            outputs = tokens
        self.convert_back(outputs)
        res = ' '.join(outputs)
        return res

    def extract_actors(self, line, noun_map, act):
        # print("Roles sentence: ", line)
        nlp_output = analyze(line)
        if nlp_output is None:
            # print(line, ": NLP API returns None. skip!")
            return ''

        # print nlp_output
        pt = parsePosTag(nlp_output)
        # print("Roles Pos Tags: ", pt)

        # get all nouns
        nouns = set()
        if 'NN' in pt:
            for pair in pt['NN']:
                nouns.add(pair[0])
        if 'NNS' in pt:
            for pair in pt['NNS']:
                nouns.add(pair[0])
        if 'NNP' in pt:
            for pair in pt['NNP']:
                nouns.add(pair[0])
        if 'NNPS' in pt:
            for pair in pt['NNPS']:
                nouns.add(pair[0])

        # print("Unsorted nouns index in role: ", nouns)
        sorted(nouns)
        # print("Sorted nouns index in role: ", nouns)
        # exit(1)

        tokens = nlp_output['sentences'][0]['tokens']
        for actor in nouns:
            actor = tokens[actor - 1]['word']
            if actor in noun_map:
                act.append(noun_map[actor])
            else:
                act.append([actor])

        # print("Actors: ", act)

    def convert_back(self, tokens):
        for i, token in enumerate(tokens):
            if token == "-LRB-":
                tokens[i] = "("
            elif token == "-RRB-":
                tokens[i] = ")"


    def detectSlash(self, sentences):
        # sentences is a list with only one sentence inside !!!!!
        temp = set()
        for i in sentences:
            print(i)
            if '/' in i:
                print(re.search('(([a-zA-Z!#%]+)/[a-zA-Z!#%]+)',i))
                match = re.search('(([a-zA-Z!#%]+)/[a-zA-Z!#%]+)',i).group(0)
                print(match)
                spl = match.split('/')
                temp.add(i.replace(match,spl[0]))
                temp.add(i.replace(match,spl[1]))
            else:
                return sentences
        return self.detectSlash(temp)



    def removeSlash(self, line, CONNECTOR) :
        # if '/' not in line :
        #     return line
        # pattern1 = '(\w)\s*' + re.escape('/')
        # pattern2 = re.escape('/') + '\s*(\S)'
        # if re.search(pattern1, line): 
        #     line = re.sub(pattern1, rf'\1 ,', line)
        # if re.search(pattern2, line): 
        #     line = re.sub(pattern2, rf', \1', line)
        # return line
        sen = line
        output = analyze(line)
        info = output['sentences'][0]['enhancedDependencies']
        print(info)
        for i in info:
            dependency = i['dep']

            if 'compound' in dependency or dependency == 'amod':
                origin = i['governorGloss'] + ' ' + i['dependentGloss']

                replace = i['governorGloss'] + CONNECTOR + i['dependentGloss']
                print(sen)
                sen = sen.replace(origin,replace)
                print(sen)

        while True:
            if ' / ' in sen:
                sen = sen.replace(' / ','/')
            elif ' /' in sen:
                sen = sen.replace(' /','/')
            elif '/ ' in sen:
                sen = sen.replace('/ ','/')
            else:
                break

        temp = self.detectSlash([sen])
        output = []
        for j in temp:
            output.append(j.replace('!#%',' '))
        return output

    def removeBracket(self, line) :
        index1 = sorted([i for i, ltr in enumerate(line) if ltr == '(' ])
        index2 = sorted([i for i, ltr in enumerate(line) if ltr == ')' ])
        if index1 == [] or index2 == []:
           return line
        sentence = ''
        previous = 0
        for i in range(0,len(index1)) :
            if index1[i]-1 >= 0 and line[index1[i]-1]== ' ' or line[index1[i]+1]==' ' :
                sentence += line[previous:index1[i]]
            else :
                sentence += line[previous:index1[i]]+' '
            previous = index2[i]+1
            if line[index2[i]-1] == ' ' or index2[i]+1 < len(line) and line[index2[i]+1] == ' ' :
                sentence += ''
            else :
                sentence += ' '
        sentence += line[index2[-1]+1:]
        if not sentence.endswith('\n') :
            sentence += '\n'
        # print(sentence)
        return sentence

        #print(index1)
        #index2 = [i for i, ltr in enumerate(line) if ltr == ')']
        
        #doc = nlp(line) 
        #result_line = []
        #remove_index = []
        #for w in doc :
        #    if w.text.startswith('('):
        #        remove_index.append(w.i)
        #    elif w.text.startswith(')'):
        #        remove_index.append(w.i)
        #    else :
        #        continue
        #if remove_index == [] :
        #    return line
        #sentence = ''

        #if remove_index[0] == 0 :
        #    sentence_start = remove_index[1] +1
        #    index_start = 2
        #else :
        #    sentence_start = 0
        #    index_start = 0

        #for i in range(index_start,len(remove_index)) :
        #    if i % 2 != 0 :
        #        sentence_start = remove_index[i]+1
        #    else :
        #        sentence += doc[sentence_start:remove_index[i]].text + ' '
        #sentence += doc[remove_index[-1]+1:len(doc)].text

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Preprocessing')
    parser.add_argument('-i', '--input', type=str, metavar='', default="./output/misspelling_detect_1/",
                        help='input path. Default: %(default)s')
    parser.add_argument('-f', '--file', type=str, metavar='',
                        help='input file. Example: python3 preprocessor.py -f 2014-USC-Projecct02')
    parser.add_argument('-o', '--output', type=str, metavar='', default="./output/preprocessing_2/",
                        help='output path. Default: %(default)s')
    parser.add_argument('-l', '--list', action='store_true',
                        help='list all input files. Example: python3 preprocessing.py -l')
    args = parser.parse_args()

    if args.file:
        filename = args.file
        input_path = args.input + filename + ".corrected.txt"
        output_path = args.output + filename

        logger = Logger(output_path + '_log.txt')

        p = PreProcessor()
        p.pre_process(input_path, output_path)
      
    elif args.list:
        input_path = args.input
        files = os.listdir(input_path)
        f_list = set()
        pattern = '.corrected.txt'
        for f in files:
            if re.search(pattern, f):
                f_list.add(re.sub(pattern, rf"", f))
        for f in sorted(f_list):
            print(f)  

    else:
        parser.print_help()


    

