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
        output = open(os.getcwd() + "/input/" + os.path.basename(self.file.name), "w")
        metadata = open(os.getcwd() + "/input/" + "meta_" + os.path.basename(self.file.name), "w")
        actors = open(os.getcwd() + "/input/" + "actor_" + os.path.basename(self.file.name), "w")

        line = self.file.readline().strip()
        while line:
            print "Original sentence: ", line
            meta = []

            # maps combined noun to the original nouns
            actor_map = {}
            act = []

            line = self.combine_nouns(line, meta, actor_map)
            line = self.replace_role(line, actor_map, act)
            output.write(line + "\n")
            metadata.write(meta.__str__() + "\n")
            actors.write(act.__str__() + "\n")

            print "Meta data: ", meta
            print " "

            line = self.file.readline().strip()


    # Ziyu: Due to our version(2018-10-05) of stanford corenlp, the TD result is not comprehensive and parts of
    # 'compound' info are missing, so that we cannot deliver totally correct result using this version, but if
    # we use version 2018-11-29, it can output more 'compound' pairs so that we can deliver result more correctly.
    # But still, some flaws of Stanford NLP API are detected. For example, it regards verb as noun, or noun as
    # adjective, which would lead us to wrong result anyway.
    #
    # Note: this function use a straight forward method to combine consecutive nouns: combining consecutive NN or NNP or
    # NNS or NNPS.
    def combine_nouns(self, line, meta, actor):
        nlp_output = analyze(line)
        if nlp_output is None:
            print line, ": NLP API returns None. skip!"
            return ''
        # print nlp_output

        line_index = []
        for i in range(0, len(nlp_output['sentences'][0]['tokens']) + 1):
            line_index.append(i)
        print "According index:", line_index

        pt = parsePosTag(nlp_output)
        print "POS Tags: ", pt
        td_key = pure_enhancedTD(nlp_output)
        print "Type Dependencies: ", td_key

        # Ziyu: the progress of combining nouns(NN), adjectives(JJ) and 'nmod:of' is similar to a typical leetcode
        # problem: Merge Intervals. First, we use index to represent each word in sentence, then in the following
        # functions, we detect if there are consecutive nouns and 'nmod:of' we need to combine, and record the starting
        # index and end index of every consecutive interval. Those intervals can be overlapped or not, or even exactly
        # the same, or their start index equals to end index, which does not matter. Function 'merge_intervals' will
        # handle the above cases and output non-overlapped intervals.
        #
        # Note: if you want to combine other words, please add them as a list of intervals so that the function
        # 'merge_intervals' can process it.
        intervals = []
        intervals.extend(self.combine_JJs_NNs(line_index, pt))
        intervals.extend(self.combine_nmod(td_key))
        intervals = self.merge_intervals(intervals)

        map = {}
        for pair in intervals:
            map[pair[0]] = pair[1]

        tokens = nlp_output['sentences'][0]['tokens']
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
                    cand += tokens[i - 1]['word'].capitalize()
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
                combined += tokens[i - 1]['word'].capitalize()
                i = i + 1

            actor[combined] = sub
            meta.append(sub)

        print "Combined sentence: ", new_line
        print "Combined nouns mapping: ", actor

        return str(new_line)


    # Take a list of intervals and return a list of non-overlapped intervals
    def merge_intervals(self, intervals):
        if len(intervals) <= 1:
            print "skip merging intervals."
            return intervals

        intervals.sort(key=lambda tup: (tup[0], tup[1]))
        print "sorted intervals: ", intervals

        list = []
        curr = intervals[0]
        i = 1
        while i < len(intervals):
            next = intervals[i]
            if curr[1] >= next[0]:
                tail = max(curr[1], next[1])
                curr = (curr[0], tail)
            else:
                list.append(curr)
                curr = next
            i = i + 1

        list.append(curr)

        print "merged intervals: ", list

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

        print "JJ + NN: ", list
        return list


    def replace_role(self, line, actor_map, act):
        # print line
        if line.startswith("As") or line.startswith('as'):
            line = line[2:].strip()
            if line.startswith('an'):
                line = line[2:].strip()
            elif line.startswith('a'):
                line = line[1:].strip()

            case = ''
            i = 0
            if ' I ' in line:
                case = 'I'
                # use ' I ' not 'I ', in case of 'UI '
                i = line.index(' I ')
                i = i + 1
            elif ' my ' in line:
                case = 'my'
                i = line.index(' my ')
                i = i + 1
            elif ',I ' in line:
                case = 'I'
                i = line.index(',I ')
                i = i + 1
            else:
                raise Exception('Cannot find subject in this sentence: ' + line)

            role = line[: i].strip()
            if role[len(role) - 1] == ',':
                role = role[: len(role) - 1]
            role = role[0].upper() + role[1:]

            self.extract_actors(role, actor_map, act)

            if case == 'I':
                line = role + line[i + 1:]
            elif case == 'my':
                line = role + "'s" + line[i + 2:]
            else:
                raise Exception('Cannot find the case of subject in this sentence: ' + line)


        print "Replaced sentence: ", line

        return line


    def extract_actors(self, line, actor_map, act):
        print "Roles sentence: ", line
        nlp_output = analyze(line)
        if nlp_output is None:
            print line, ": NLP API returns None. skip!"
            return ''

        # print nlp_output
        pt = parsePosTag(nlp_output)
        print "Roles Pos Tags: ", pt

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
        print "Sorted nouns index in role: ", nouns

        tokens = nlp_output['sentences'][0]['tokens']
        for actor in nouns:
            actor = tokens[actor - 1]['word']
            if actor in actor_map:
                act.append(actor_map[actor])
            else:
                act.append(actor)

        print "Actors: ", act




if __name__ == '__main__':
    p = PreProcessor(os.getcwd() + "/Data/input_origin/" + "2014-USC-Project02.txt")
    # p = PreProcessor(os.getcwd() + "/Data/input_origin/" + "test.txt")
    p.pre_process()


