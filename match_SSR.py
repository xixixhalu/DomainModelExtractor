import os

from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *
from identifier import Identifier



class MatchSSR:

    def dir_path(self, directory):

        return os.getcwd() + directory

    def read_one_file(self, file_path, file_name):

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

    def query(self, tr_names, tds, pos_tags, keywords, vars, identifier, input):
        line = input.readline().strip()
        while line:
            nlp_output = analyze(line)
            if nlp_output is None:
                print line, ": NLP API returns None. skip!"
                line = input.readline.strip()
                continue
            print " "
            print line
            if self.match_tds(tds, vars, nlp_output) is True:
                print("Matched!")
                identifier.display_sentence_index(line, nlp_output)
                for key in vars:
                    print key, vars[key]
            else:
                print "Does not match!"

            line = input.readline().strip()

    def match_tds(self, rule_tds, rule_vars, nlp_output):
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
            return False

        # clear rule variables mapping before each dfs
        for key in rule_vars:
            rule_vars[key] = None

        if self.dfs_match_tds(rule_tds, td_key, 0, {}, {}, rule_vars) is True:
            return True

        return False

    def dfs_match_tds(self, rule_tds, text_tds, rule_pos, var_to_index, index_to_var, rule_vars):
        if rule_pos == len(rule_tds):
            for key in var_to_index:
                rule_vars[key] = var_to_index[key]

            return True

        key_to_match = rule_tds[rule_pos][0]
        var1 = rule_tds[rule_pos][1]
        var2 = rule_tds[rule_pos][2]
        for candidate_index in text_tds[key_to_match]:
            cand1 = candidate_index[0]
            cand2 = candidate_index[1]
            if cand1 in index_to_var and index_to_var[cand1] is not var1:
                continue
            if cand2 in index_to_var is not None and index_to_var[cand2] is not var2:
                continue

            var_to_index[var1] = cand1
            var_to_index[var2] = cand2
            index_to_var[cand1] = var1
            index_to_var[cand2] = var2

            if self.dfs_match_tds(rule_tds, text_tds, rule_pos + 1, var_to_index, index_to_var, rule_vars) is True:
                return True

            var_to_index[var1] = None
            var_to_index[var2] = None
            index_to_var[cand1] = None
            index_to_var[cand2] = None

        return False


if __name__ == '__main__':
    ssr = MatchSSR()
    identifier = Identifier()
    # read rule
    rule_path = ssr.dir_path("/SSR/")
    rule_obj = ssr.read_one_file(rule_path, "SSR1.txt")
    rule_result = ssr.parse_rule(rule_obj)
    rule_obj.close()
    # split rule result
    rule_name = rule_result[0]
    rule_TD_list = rule_result[1]
    rule_POS_dict = rule_result[2]
    rule_keywords = rule_result[3]
    rule_var_map = rule_result[4]
    # read sentences
    dir_path = ssr.dir_path("/Data/input_origin/")
    req_obj = ssr.read_one_file(dir_path, "test.txt")
    ssr.query(rule_name, rule_TD_list, rule_POS_dict, rule_keywords, rule_var_map, identifier, req_obj)
    req_obj.close()
