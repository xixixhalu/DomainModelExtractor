import os

from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *


# create a class to pre-process
# 1. replace I with role
# 2. combine consecutive Nouns
# 3. output another identical file


class PreProcessor:

    def __init__(self, file_path):
        self.file = open(file_path)

    def pre_process(self):
        # overwrite previous output file
        dirs = os.getcwd() + "/input_v2/"
        if not os.path.exists(dirs):
            os.makedirs(dirs)

        output = open(dirs + os.path.basename(self.file.name), "w")
        metadata = open(dirs + "meta_" + os.path.basename(self.file.name), "w")
        actors = open(dirs + "actor_" + os.path.basename(self.file.name), "w")

        line = self.file.readline().strip()
        while line:
            # print("Original sentence: ", line)
            meta = []

            # maps combined noun to the original nouns
            actor_map = {}
            act = []
            line = self.combine_nouns(line, meta, actor_map)
            line = self.replace_role(line, actor_map, act)
            output.write(line + "\n")
            metadata.write(meta.__str__() + "\n")
            actors.write(act.__str__() + "\n")

            # print("Meta data: ", meta)
            # print(" ")

            line = self.file.readline().strip()

        output.close()
        metadata.close()
        actors.close()

    # Note: this function use a straight forward method to combine consecutive nouns: combining consecutive NN or NNP or
    # NNS or NNPS.
    def combine_nouns(self, line, meta, actor):
        nlp_output = analyze(line)
        if nlp_output is None:
            # print(line, ": NLP API returns None. skip!")
            return ''
        # print nlp_output

        line_index = []
        for i in range(0, len(nlp_output['sentences'][0]['tokens']) + 1):
            line_index.append(i)
        # print("According index:", line_index)

        pt = parsePosTag(nlp_output)
        # print("POS Tags: ", pt)
        td_key = pure_enhancedTD(nlp_output)
        # print("Type Dependencies: ", td_key)

        # Note: if you want to combine other words, please add them as a list of intervals so that the function
        # 'merge_intervals' can process it.
        intervals = []
        intervals.extend(self.combine_JJs_NNs(line_index, pt))
        intervals.extend(self.combine_nmod(td_key))
        intervals = self.merge_intervals(intervals)

        tokens = nlp_output['sentences'][0]['tokens']

        intervals = self.check_intervals(intervals, tokens)

        map = {}
        for pair in intervals:
            map[pair[0]] = pair[1]

        new_line = ''
        i = 1

        # construct combined sentence
        while i < len(line_index):
            cand = tokens[i - 1]['word']

            if i in map:
                cand = cand.capitalize()
                j = map[i]
                i = i + 1
                while i <= j:
                    cand += tokens[i - 1]['word'][0].upper() + tokens[i - 1]['word'][1:]
                    i = i + 1

                i = i - 1

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
                sub.append(tokens[i - 1]['word'])
                combined += tokens[i - 1]['word'][0].upper() + tokens[i - 1]['word'][1:]
                i = i + 1

            actor[combined] = sub
            meta.append((sub, pair))

        # print("Combined sentence: ", new_line)
        # print("Combined nouns mapping: ", actor)

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

    def check_intervals(self, intervals, tokens):
        '''
        This function is responsible for filtering invalidate intervals to assist future steps.
        All invalidate words are included in key_words and key_phrase_words.
        Please note that this function exploit lemmatization from Stanford NLP API, so users do not need to care about
        words' inflection.

        1. If an interval contains a word in key_words called key, this function will use all the words after key to
        construct an new interval to replace the original one.

        2. If an interval contains a word in key_phrase_words and and its next word is "of", this function will also
        remove them as well as construct an new one.

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
        key_words = ["include", "extend", "resume", "repeat", "contain"]
        key_phrase_words = ["part", "unit", "member", "consist", "make", "compose", "type", "kind", "parent"]

        def combine_tokens(interval, tokens):
            res = []
            for i in range(interval[0], interval[1] + 1):
                token = tokens[i-1]['lemma'].lower()
                res.append(token)
            return res

        for interval in intervals:
            candidates = combine_tokens(interval, tokens)
            start = interval[0]
            end = interval[1]
            for i, word in enumerate(candidates):
                if word in key_words:
                    start = start + i + 1
                elif word in key_phrase_words:
                    if i + 1 < len(candidates) and candidates[i+1] == 'of':
                        start = start + i + 2
            start_word = tokens[start - 1]['word']
            if start_word == 'the' or start_word == 'an' or start_word == 'a':
                start = start + 1
            _intervals.append((start, end))

        return _intervals

    # Return a list of index intervals that we should combine
    def combine_nmod(self, td_key):
        list = []
        if 'nmod:of' in td_key:
            for pair in td_key['nmod:of']:
                p1 = min(pair[0], pair[1])
                p2 = max(pair[0], pair[1])
                list.append((p1, p2))

        return list

    # Return a list of index intervals that we should combine
    def combine_JJs_NNs(self, line_index, pt):
        # Add all NN or NNP or NNS or NNPS to a set
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

        # Add all JJ to a set
        adjs = set()
        if 'JJ' in pt:
            for pair in pt['JJ']:
                adjs.add(pair[0])

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

    def replace_role(self, line, actor_map, act):
        nlp_output = analyze(line)
        noun_set = {'NN', 'NNP', 'NNS', 'NNPS'}
        tokens = [d['word'] for d in nlp_output['sentences'][0]['tokens']]
        pos_tags = [d['pos'] for d in nlp_output['sentences'][0]['tokens']]
        outputs = []
        if tokens[0] == 'As' or tokens[0] == 'as':
            if tokens[1] == 'a' or tokens[1] == 'an':
                idx = 2
            else:
                idx = 1
            while idx < len(pos_tags) and pos_tags[idx] not in noun_set:
                idx += 1
            role = tokens[idx]
            outputs.extend(tokens[idx + 1:])
            if outputs[0] == ',':
                outputs = outputs[1:]

            def index(tokens, original, replace):
                for i, token in enumerate(tokens):
                    if token == original:
                        tokens[i] = replace

            self.extract_actors(role, actor_map, act)
            subjects = ['I', 'i', 'we', 'We']
            for subject in subjects:
                index(outputs, subject, role)
            pronouns = ['my']
            for pronoun in pronouns:
                index(outputs, pronoun, role + "'s")
        else:
            outputs = tokens
        self.convert_back(outputs)
        res = ' '.join(outputs)
        return res

    def extract_actors(self, line, actor_map, act):
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

        # print "Unsorted nouns index in role: ", nouns
        sorted(nouns)
        # print("Sorted nouns index in role: ", nouns)

        tokens = nlp_output['sentences'][0]['tokens']
        for actor in nouns:
            actor = tokens[actor - 1]['word']
            if actor in actor_map:
                act.append(actor_map[actor])
            else:
                act.append(actor)

        # print("Actors: ", act)

    def convert_back(self, tokens):
        for i, token in enumerate(tokens):
            if token == "-LRB-":
                tokens[i] = "("
            elif token == "-RRB-":
                tokens[i] = ")"


if __name__ == '__main__':

    # p = PreProcessor(os.getcwd() + "/Data/input_origin/" + "test.txt")

    # for year in range(2014, 2020):
    #     for project in range(1, 16):
    #         file_name = str(year) + '-USC-Project' + str(project).rjust(2, '0')
    #         file_path = os.getcwd() + "/Data/input_origin/" + file_name + '.txt'
    #         if not os.path.exists(file_path):
    #             continue
    #         print("processing " + file_path)
    #         p = PreProcessor(file_path)
    #         p.pre_process()

    file_path = os.getcwd() + "/Data/input_origin/test.txt"
    print("processing " + file_path)
    p = PreProcessor(file_path)
    p.pre_process()

