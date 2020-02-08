import os

from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *
from identifier import Identifier
import pandas as pd
import re


# create a class Matcher here and store identifier and input in it
class Matcher:

    # internal class to store the matched result
    class MatchedSentence:

        def __init__(self, sentence, tokens, var_map):
            self.sentence = sentence
            self.tokens = tokens
            self.var_map = var_map

        def __repr__(self):
            return "Sentence: %s\nTokens: %s\nVariables: %s\n" %(self.sentence, self.tokens, self.var_map)


    def __init__(self, identifier, sentences_file_path):
        self.identifier = identifier
        self.sentences_file = self.read_one_file(sentences_file_path)


    def dir_path(self, directory):

        return os.getcwd() + directory


    def read_one_file(self, file_path, file_name = None):
        if file_name is None:
            return open(file_path)
        else:
            return open(file_path + file_name)


    # Note: this parser assumes that input is written correctly and completely
    def parse_rule(self, file_obj, rule):
        rule = 'SSR' + str(rule)
        rule_name = ''
        rule_TD_list = []
        rule_POS_dict = {}
        rule_keywords = []

        try:
            line = file_obj.loc[rule]
        except:
            print('No such a RULE! Please try another RULE!')
            rule = input('No such a RULE! Please try another RULE!\nEnter:')
            self.parse_rule(rule_obj, int(rule))

        # read name
        rule_name = line.loc['Sentence Structure']

        # read TD rules
        TDs = line.loc['TDs']
        if str(TDs) == 'nan':
            print("TD rule is empty")
        else:
            TDs_sep = re.split('[(,)]', TDs)
            TDs_sep = [TD for TD in TDs_sep if TD != '']
            # since format of TD rule is "rule_name(var1,var2)"
            length = len(TDs_sep)
            for i in range(0, length, 3):
                td_name = TDs_sep[i]
                var1 = TDs_sep[i + 1]
                var2 = TDs_sep[i + 2]
                tup = (td_name, var1, var2)
                rule_TD_list.append(tup)

        # read POS rule
        POS_tags = line.loc['POS-tags']
        if str(POS_tags) == 'nan':
            print("POS-tag rule is empty")
        else:
            pos_list = POS_tags.split("==")
            pos_var = pos_list[0].strip()
            pos_type = pos_list[1].strip()
            rule_POS_dict[pos_var] = pos_type

        # read start word
        startword = line.loc['start word']
        if str(startword) == 'nan':
            print("Start word is empty")
        else:
            rule_keywords.append(startword)

        print("\n======== parsed rule ========")
        print("rule name: ", rule_name)
        print("TD list: ", rule_TD_list)
        print("POS-tag list: ", rule_POS_dict)
        print("Keywords: ", rule_keywords)

        return rule_name, rule_TD_list, rule_POS_dict, rule_keywords


    def query(self, tr_names, tds, pos_tags, keywords):
        print("\n======== process sentences ========")
        res = []
        line = self.sentences_file.readline().strip()
        while line:
            nlp_output = analyze(line)
            if nlp_output is None:
                print(line, ": NLP API returns None. skip!")
                line = input.readline.strip()
                continue
            print(line)
            td_res = self.match_tds(tds, nlp_output)
            if td_res[0] and self.match_pos(td_res[1], pos_tags, nlp_output) and self.match_keywords(line, keywords):
                res.append(self.MatchedSentence(line, self.build_tokens(nlp_output), td_res[1]))
            print(" ")
            line = self.sentences_file.readline().strip()

        return res


    def build_tokens(self, nlp_output):
        tokens = {}
        for t in nlp_output['sentences'][0]['tokens']:
            tokens[t['index']] = t['word']

        return tokens


    # Note: A sentence should start with the keyword, if we have keyword in rule to match. And parameter keywords
    # is a list, it should only contains one element.(since one sentence cannot start with two different words)
    # Return: When the string starts with this keyword, return True; otherwise, return False.
    def match_keywords(self, line, keywords):
        flag = True
        for word in keywords:
            if not line.startswith(word):
                flag = False
                break

        return flag


    def match_pos(self, var_map, rule_pos_tag, nlp_output):
        pt = parsePosTag(nlp_output)
        # init flag to True here to handle the case that rule_pos_tag is empty
        flag = True
        for var in rule_pos_tag:
            flag = False
            var_pos = rule_pos_tag[var]
            if var_pos not in pt:
                break
            for cand_tup in pt[var_pos]:
                # find it
                # Ziyu: only when the two elements in tup are the same, it might be true.
                if cand_tup[0] == cand_tup[1] and cand_tup[0] == var_map[var]:
                    flag = True
                    break
            if not flag:
                break

        return flag


    def match_tds(self, rule_tds, nlp_output):
        td_key = enhancedTD(nlp_output)
        print(td_key)
        # check number of TDs
        td_count = {}
        for tup in rule_tds:
            td_count[tup[0]] = 1 + td_count.get(tup[0], 0)
        flag = True
        for key in td_count:
            if td_key.get(key) is None or len(td_key.get(key)) < td_count.get(key):
                flag = False
                break
        if not flag:
            return False, None

        return self.dfs_match_tds(rule_tds, td_key, 0, {}, {})

    # Note: the assumption here is that variables and indexes are 1 to 1 mapping. Each variable is mapped to only one
    # unique index.
    def dfs_match_tds(self, rule_tds, text_tds, rule_pos, var_to_index, index_to_var):
        if rule_pos == len(rule_tds):

            return True, var_to_index

        key_to_match = rule_tds[rule_pos][0]
        var1 = rule_tds[rule_pos][1]
        var2 = rule_tds[rule_pos][2]
        for candidate_index in text_tds[key_to_match]:
            cand1 = candidate_index[0]
            cand2 = candidate_index[1]

            # If one of the candidate index has been assigned to a variable before, and that variable is not the same as
            # the current variable we are going to match, which means that we are going to assign one index to two
            # different variables, and such situation violates the 1:1 mapping assumption. We skip this candidate.
            if cand1 in index_to_var and index_to_var[cand1] is not None and index_to_var[cand1] is not var1:
                continue
            if cand2 in index_to_var and index_to_var[cand2] is not None and index_to_var[cand2] is not var2:
                continue

            # If one of the variable has been assigned to an index, and the assigned index is not the same as the
            # current "candidate" index, which means that we are going to assign two different indexes to one variable,
            # which violates the 1:1 mapping assumption. We skip this candidate index.
            if var1 in var_to_index and var_to_index[var1] is not None and var_to_index[var1] is not cand1:
                continue
            if var2 in var_to_index and var_to_index[var2] is not None and var_to_index[var2] is not cand2:
                continue

            var_to_index[var1] = cand1
            var_to_index[var2] = cand2
            index_to_var[cand1] = var1
            index_to_var[cand2] = var2

            # Ziyu: it only output the first valid result
            if self.dfs_match_tds(rule_tds, text_tds, rule_pos + 1, var_to_index, index_to_var)[0] is True:
                return True, var_to_index

            var_to_index[var1] = None
            var_to_index[var2] = None
            index_to_var[cand1] = None
            index_to_var[cand2] = None

        return False, var_to_index


if __name__ == '__main__':
    # create a Matcher object which is initialized with Identifier and input file path
    ssr = Matcher(Identifier(), os.getcwd() + "/Data/input_origin/" + "test.txt")
    # read rule
    rule_path = ssr.dir_path("\\SSR\\")
    rule_obj = pd.read_csv(rule_path + "SSR.csv")
    rule_obj.set_index(["Rule"], inplace=True)
    rule_result = ssr.parse_rule(rule_obj, 30)
    # split rule result
    rule_name = rule_result[0]
    rule_TD_list = rule_result[1]
    rule_POS_dict = rule_result[2]
    rule_keywords = rule_result[3]

    res = ssr.query(rule_name, rule_TD_list, rule_POS_dict, rule_keywords)
    print("======== matched sentences ========")
    for r in res:
        print(r)