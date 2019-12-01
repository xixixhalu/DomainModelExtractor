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

        line = self.file.readline().strip()
        while line:
            print line
            meta = []
            print "combie nouns"
            line = self.combine_nouns(line, meta)
            print "combie nmod"
            line = self.combine_nmod(line, meta)
            print "replace role"
            line = self.replace_role(line)
            output.write(line + "\n")
            metadata.write(meta.__str__() + "\n")

            print "meta: ", meta
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
    def combine_nouns(self, line, meta):
        nlp_output = analyze(line)
        if nlp_output is None:
            print line, ": NLP API returns None. skip!"
            return ''
        print nlp_output

        pt = parsePosTag(nlp_output)
        print pt
        td_key = pure_enhancedTD(nlp_output)
        print td_key

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
                combined_noun_sub = []
                combined_noun_sub.append(cand)
                j = i + 1
                while j in nouns:
                    if j == i + 1:
                        cand = cand.capitalize()
                    cand += tokens[j - 1]['word'].capitalize()
                    combined_noun_sub.append(tokens[j - 1]['word'])
                    j = j + 1

                if j > i + 1:
                    i = j - 1
                if len(combined_noun_sub) > 1:
                    meta.append(combined_noun_sub)

            if cand == ',' or cand == '.':
                new_line = new_line.strip()
            new_line += cand
            if cand != '`':
                new_line += ' '
            i = i + 1

        new_line = new_line.strip()

        # print line
        print new_line
        print meta

        return str(new_line)



    def combine_nmod(self, line, meta):
        nlp_output = analyze(line)
        if nlp_output is None:
            print line, ": NLP API returns None. skip!"
            return ''
        print nlp_output

        td_key = pure_enhancedTD(nlp_output)
        print td_key

        if 'nmod:of' not in td_key:
            return line

        map = {}
        for p in td_key['nmod:of']:
            p1 = min(p[0], p[1])
            p2 = max(p[0], p[1])
            map[p1] = p2


        line_index = []
        for i in range(0, len(nlp_output['sentences'][0]['tokens']) + 1):
            line_index.append(i)

        print line
        print line_index
        print "map: ", map

        tokens = nlp_output['sentences'][0]['tokens']
        new_line = ''
        i = 1

        while i < len(line_index):
            cand = tokens[i - 1]['word']

            if i in map:
                combined_noun_sub = []
                combined_noun_sub.append(cand)
                cand = cand.capitalize()
                j = map[i]
                i = i + 1
                while i <= j:
                    cand += tokens[i - 1]['word'].capitalize()
                    combined_noun_sub.append(tokens[i - 1]['word'])
                    i = i + 1

                meta.append(combined_noun_sub)
                i = i - 1

            if cand == ',' or cand == '.':
                new_line = new_line.strip()
            new_line += cand
            if cand != '`':
                new_line += ' '
            i = i + 1

        print new_line
        print meta

        return str(new_line)


    def replace_role(self, line):
        # print line
        if line.startswith("As") or line.startswith('as'):
            line = line[2:].strip()
            if line.startswith('an'):
                line = line[2:].strip()
            elif line.startswith('a'):
                line = line[1:].strip()

            # use ' I ' not 'I ', in case of 'UI '
            i = line.index(' I ')
            i = i + 1
            role = line[: i].strip()
            if role[len(role) - 1] == ',':
                role = role[: len(role) - 1]
            role = role[0].upper() + role[1:]
            line = role + line[i + 1:]

        print line
        return line




if __name__ == '__main__':
    # p = PreProcessor(os.getcwd() + "/Data/input_origin/" + "2014-USC-Project01.txt")
    p = PreProcessor(os.getcwd() + "/Data/input_origin/" + "test.txt")
    p.pre_process()


