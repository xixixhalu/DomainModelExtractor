import sys
sys.path.append('./')
sys.path.append('../')

import os
from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *
from identifier import Identifier
import pandas as pd
import re
from tqdm import tqdm



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

    def __init__(self, identifier, sentence):
        self.identifier = identifier
        self.sentence = sentence.strip()

    # Note: this parser assumes that input is written correctly and completely
    # To obtain rule info of a certain SSR
    def parse_rule(self, file_obj, rule):  # file_obj is supposed to be a DataFrame storing all SSR info; rule is the rule No.
        # variable initialization
        rule = 'SSR' + str(rule)
        rule_name = ''
        rule_TD_list = []
        rule_POS_dict = {}
        rule_keywords = []

        try:  # make sure we have a valid rule
            line = file_obj.loc[rule]
        except:
            print('No such a RULE! Please try another RULE!')
            rule = input('No such a RULE! Please try another RULE!\nEnter:')
            self.parse_rule(rule_obj, int(rule))

        # read the rule name
        rule_name = line.loc['Sentence Structure'].strip()

        # read TD rule of current SSR
        TDs = line.loc['TDs']
        if str(TDs) != 'nan':
            TDs_sep = re.split('[(,)]', TDs)
            TDs_sep = [TD for TD in TDs_sep if TD != '']
            # put current TD structured in a listsince format of TD rule is "TD_name(var1,var2)"
            # e.g. [('nsubj', 'A', 'B'), ('iobj', 'A', 'C'), ('dobj', 'A', 'D')] for SSR1
            length = len(TDs_sep)
            for i in range(0, length, 3):
                td_name = TDs_sep[i].strip()
                var1 = TDs_sep[i + 1].strip()
                var2 = TDs_sep[i + 2].strip()
                tup = (td_name, var1, var2)
                rule_TD_list.append(tup)

        # read POS rule of current SSR
        POS_tags = line.loc['POS-tags']
        if str(POS_tags) != 'nan':
            pos_list = POS_tags.split("==")
            pos_var = pos_list[0].strip()
            pos_type = pos_list[1].strip()
            rule_POS_dict[pos_var] = pos_type

        # read start word
        startword = line.loc['start word']
        if str(startword) != 'nan':
            rule_keywords.append(startword.strip())

        # print("\n======== parsed rule ========")
        # print("rule name: ", rule_name)
        # print("TD list: ", rule_TD_list)
        # print("POS-tag list: ", rule_POS_dict)
        # print("Keywords: ", rule_keywords)

        return rule_name, rule_TD_list, rule_POS_dict, rule_keywords

    # Note: A sentence should start with the keyword, if we have keywords in a rule to match. And parameter keywords
    # is a list, it should only contains one element.(since one sentence cannot start with two different words)
    # Return: When the string starts with this keyword, return True; otherwise, return False.
    def match_keywords(self, line, rule_keywords):
        flag = True
        for word in rule_keywords:
            if not line.startswith(word):
                flag = False
                break

        return flag

    # nlp_output is the result of sentence from Stanford NLP.
    def match_pos(self, var_map, rule_pos_tags, nlp_output):
        pt = parsePosTag(nlp_output)  # obtain POS-tags from Stanford NLP
        # init flag to True here to handle the case that rule_pos_tag is empty
        flag = True
        for var in rule_pos_tags:
            flag = False
            var_pos = rule_pos_tags[var]
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

    # rule_tds is the TD of SSR
    def match_tds(self, rule_tds, td_key):
        # check number of TDs
        td_count = {}
        for tup in rule_tds:
            td_count[tup[0]] = 1 + td_count.get(tup[0], 0)

        flag = True
        for key in td_count:
            if td_key.get(key) is None or len(td_key.get(key)) < td_count.get(key):
                flag = False
                break

        # when flag == False
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

    # read rule
    rule_obj = pd.read_excel(os.getcwd() + "/../SSR/" + "update_SSR.xlsx")
    rule_obj.set_index(["Rule"], inplace=True)

    allResult = dict()
    # travel each file
    for year in tqdm(range(2014, 2020)):
        for projectnum in range(1, 16):
            file_name = str(year) + '-USC-Project' + str(projectnum).rjust(2, '0') + '.txt'
            file_path = os.getcwd() + "/../input_v2/" + file_name
            if not os.path.exists(file_path):  # examine whether the filename is valid
                break
            else:  # when the filename is valid
                with open(file_path, 'r') as f:
                    content = f.readlines()
                    for s in range(len(content)):  # format sentences
                        content[s] = content[s].strip()

                    result_file = []
                    for j in range(len(content)):  # travel each sentence to match SSR
                        # the sentence we want to test
                        sentence = content[j]
                        ssr = Matcher(Identifier(), sentence)
                        nlp_output = analyze(sentence)  # use Stanford NLP to parse

                        result = []  # to store all matched SSRs NO.
                        if nlp_output is None:
                            print(sentence, ": NLP API returns None!")
                            result.append([])
                        else:
                            match_ssr = []  # to store matched SSR
                            td_key = enhancedTD(nlp_output)
                            #print(td_key)

                            for i in range(1, 34):  # travel each SSR
                                rule_result = ssr.parse_rule(rule_obj, i)
                                # split rule result
                                rule_name = rule_result[0]
                                rule_tds = rule_result[1]
                                rule_pos_tags = rule_result[2]
                                rule_keywords = rule_result[3]

                                td_res = ssr.match_tds(rule_tds, td_key)
                                if td_res[0] and ssr.match_pos(td_res[1], rule_pos_tags, nlp_output) and ssr.match_keywords(ssr.sentence,rule_keywords):
                                    match_ssr.append(i)
                            result.extend(match_ssr)
                        result_file.append(result)
                    allResult[file_name] = result_file

    output = json.dumps(allResult, indent=4)
    with open('allFileMatchResult_v2.json', 'w') as json_file:
        json_file.write(output)
