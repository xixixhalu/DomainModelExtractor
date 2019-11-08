import os

from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *
from identifier import Identifier


class Matcher:

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
    def parse_rule(self, file_obj):
        rule_name = ""
        rule_TD_list = []
        rule_POS_dict = {}
        rule_keywords = []
        rule_var_map = {}

        line = file_obj.readline().strip()
        # read name
        if line == "#":
            print "SSR name is empty"
        else:
            rule_name = line

        # read TD rules
        file_obj.readline()
        line = file_obj.readline().strip()
        if line == "#":
            print "TD rule is empty"
            file_obj.readline()
        else:
            while line != "\n":
                line = line.strip()
                # since format of TD rule is "rule_name(var1,var2)"
                idx = line.find("(")
                td_name = line[0:idx]
                idx2 = line.find(",")
                var1 = line[idx + 1:idx2].strip()
                idx = line.find(")")
                var2 = line[idx2 + 1:idx].strip()
                tup = (td_name, var1, var2)
                rule_TD_list.append(tup)
                rule_var_map[var1] = "";
                rule_var_map[var2] = "";

                line = file_obj.readline()

        # read POS rule
        line = file_obj.readline().strip()
        if line == "#":
            print "POS-tag rule is empty"
            file_obj.readline()
        else:
            while line != "\n":
                line = line.strip()
                pos_list = line.split("=")
                pos_var = pos_list[0].strip()
                pos_type = pos_list[1].strip()
                rule_POS_dict[pos_var] = pos_type

                line = file_obj.readline()

        # read keywords
        line = file_obj.readline().strip()
        if line == "#":
            print "Keyword is empty"
        else:
            while line and line != "\n":
                line = line.strip()
                rule_keywords.append(line)
                line = file_obj.readline()

        # print parsed result
        print "\n======== parsed rule ========"
        print "rule name: ", rule_name
        print "TD list: ", rule_TD_list
        print "POS-tag list: ", rule_POS_dict
        print "Keywords: ", rule_keywords
        print "Variables: ", rule_var_map

        return rule_name, rule_TD_list, rule_POS_dict, rule_keywords, rule_var_map


    # create a class Matcher here and store identifier and input in it
    # remove vars
    def query(self, tr_names, tds, pos_tags, keywords):
        print "\n======== process sentences ========"
        line = self.sentences_file.readline().strip()
        while line:
            nlp_output = analyze(line)
            if nlp_output is None:
                print line, ": NLP API returns None. skip!"
                line = input.readline.strip()
                continue
            print " "
            print line
            td_res = self.match_tds(tds, nlp_output)
            if td_res[0] is True:
                print("TD Matched!")
                self.identifier.display_sentence_index(line, nlp_output)
                var_map = td_res[1]
                for key in var_map:
                    print key, var_map[key]
            else:
                print "TDs Do not match!"

            line = self.sentences_file.readline().strip()


    def match_tds(self, rule_tds, nlp_output):
        td_key = enhancedTD(nlp_output)
        print td_key

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



    def dfs_match_tds(self, rule_tds, text_tds, rule_pos, var_to_index, index_to_var):
        if rule_pos == len(rule_tds):

            return True, var_to_index

        key_to_match = rule_tds[rule_pos][0]
        var1 = rule_tds[rule_pos][1]
        var2 = rule_tds[rule_pos][2]
        for candidate_index in text_tds[key_to_match]:
            cand1 = candidate_index[0]
            cand2 = candidate_index[1]
            if cand1 in index_to_var and index_to_var[cand1] is not None and index_to_var[cand1] is not var1:
                continue
            if cand2 in index_to_var and index_to_var[cand2] is not None and index_to_var[cand2] is not var2:
                continue
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
    rule_path = ssr.dir_path("/SSR/")
    rule_obj = ssr.read_one_file(rule_path, "SSR6.txt")
    rule_result = ssr.parse_rule(rule_obj)
    rule_obj.close()
    # split rule result
    rule_name = rule_result[0]
    rule_TD_list = rule_result[1]
    rule_POS_dict = rule_result[2]
    rule_keywords = rule_result[3]
    # TODO: eliminate var_map
    rule_var_map = rule_result[4]

    ssr.query(rule_name, rule_TD_list, rule_POS_dict, rule_keywords)
