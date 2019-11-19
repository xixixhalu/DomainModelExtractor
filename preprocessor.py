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

        line = self.file.readline().strip()
        while line:
            print line
            line = self.combine_nouns(line)
            line = self.replace_role(line)
            output.write(line + "\n")
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
    def combine_nouns(self, line):
        nlp_output = analyze(line)
        if nlp_output is None:
            print line, ": NLP API returns None. skip!"
            return ''
        print nlp_output

        pt = parsePosTag(nlp_output)
        print pt
        # td_key = enhancedTD(nlp_output)
        # print td_key

        line_index = []
        for i in range(0, len(nlp_output['sentences'][0]['tokens']) + 1):
            line_index.append(i)
        print line_index

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

        tokens = nlp_output['sentences'][0]['tokens']
        new_line = ''
        i = 1

        while i < len(line_index):
            cand = tokens[i - 1]['word']

            if i in nouns:
                j = i + 1
                while j in nouns:
                    if j == i + 1:
                        cand = cand.capitalize()
                    cand += tokens[j - 1]['word'].capitalize()
                    j = j + 1

                if j > i + 1:
                    i = j - 1

            if cand == ',' or cand == '.':
                new_line = new_line.strip()
            new_line += cand
            if cand != '`':
                new_line += ' '
            i = i + 1

        new_line = new_line.strip()

        # print line
        print new_line

        return new_line

        # Ziyu: the following code implements 'combine_nouns' function by using 'compound', which is not good enough, so
        # I comment them out.

        # # A kind of Union Find. 'compound' nouns have the same parent(only one level indirection)
        # for pair in td_key['compound']:
        #     parent = pair[0]
        #     child = pair[1]
        #     line_index[parent] = parent
        #     line_index[child] = parent
        # print line_index
        #
        # new_line = ''
        # i = 1
        # while i < len(line_index):
        #     cand = nlp_output['sentences'][0]['tokens'][i - 1]['word']
        #
        #     # TODO: should we also check that they are NN or NNS or NNP or NNPS? I think if one word is in the pair of 'compound', it must be a kind of Noun
        #     # Check if we can form a compound noun
        #     j = i + 1
        #     while j < len(line_index) and line_index[j] == line_index[j - 1]:
        #         if j == i + 1:
        #             cand = cand.capitalize()
        #         cand += nlp_output['sentences'][0]['tokens'][j - 1]['word'].capitalize()
        #         j = j + 1
        #
        #     if j > i + 1:
        #         i = j - 1
        #
        #     if cand == ',' or cand == '.':
        #         new_line = new_line.strip()
        #
        #     new_line += cand
        #     new_line += ' '
        #     i = i + 1
        #
        # new_line = new_line.strip()
        # print new_line


    def replace_role(self, line):
        # print line
        if line.startswith("As") or line.startswith('as'):
            line = line[2:].strip()
            if line.startswith('an'):
                line = line[2:].strip()
            elif line.startswith('a'):
                line = line[1:].strip()

            i = line.index('I ')
            role = line[: i].strip()
            if role[len(role) - 1] == ',':
                role = role[: len(role) - 1]
            role = role[0].upper() + role[1:]
            line = role + line[i + 1:]

        print line
        return line




if __name__ == '__main__':
    p = PreProcessor(os.getcwd() + "/Data/input_origin/" + "2014-USC-Project01.txt")
    # p = PreProcessor(os.getcwd() + "/Data/input_origin/" + "test.txt")
    p.pre_process()


