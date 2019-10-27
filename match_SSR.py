import os

from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *

class MatchSSR:

    def __init__(self):
        self.rule_name = "";
        self.rule_TD_list = []
        self.rule_POS_dict = {}
        self.rule_keywords = []
        self.rule_var_map = {}

    def dir_path(self, directory):

        return os.getcwd() + directory

    def read_one_file(self, file_path, file_name):

        return open(file_path + file_name)

    # Note: this parser assumes that input is written correctly and completely
    def parse_rule(self, file_obj):
        line = file_obj.readline().strip()
        # read name
        if line == "#":
            print "SSR name is empty"
        else:
            self.rule_name = line

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
                rule_name = line[0:idx]
                idx2 = line.find(",")
                var1 = line[idx + 1:idx2].strip()
                idx = line.find(")")
                var2 = line[idx2 + 1:idx].strip()
                tup = (rule_name, var1, var2)
                self.rule_TD_list.append(tup)
                self.rule_var_map[var1] = "";
                self.rule_var_map[var2] = "";

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
                self.rule_POS_dict[pos_var] = pos_type

                line = file_obj.readline()

        # read keywords
        line = file_obj.readline().strip()
        if line == "#":
            print "Keyword is empty"
        else:
            while line and line != "\n":
                line = line.strip()
                self.rule_keywords.append(line)
                line = file_obj.readline()

        # print parsed result
        print "\n======== parsed rule ========"
        print "rule name: ", self.rule_name
        print "TD list: ", self.rule_TD_list
        print "POS-tag list: ", self.rule_POS_dict
        print "Keywords: ", self.rule_keywords
        print "Variables: ", self.rule_var_map

    def match(self, file_obj):

        # preparation
        td_count = {}
        for tup in self.rule_TD_list:
            td_count[tup[0]] = 1 + td_count.get(tup[0], 0)

        line = file_obj.readline().strip()
        while line:

            nlp_output = analyze(line)
            if nlp_output is None:
                print "NLP API returns None. skip!"
                line = file_obj.readline.strip()
                continue

            # TD type as key; e.g. 'det': [(3,2), (5,4)]
            td_key = TypeDep1(nlp_output)
            # Index tuple as key; e.g. (3,2): 'det'
            idx_key = TypeDep(nlp_output)
            pt_result = parsePosTag(nlp_output)

            # check number of TDs
            flag = True
            for key in td_count:
                if td_key.get(key) is None or len(td_key.get(key)) < td_count.get(key):
                    flag = False
                    break
            if not flag:
                line = file_obj.readline().strip()
                continue
            # clear var
            for key in self.rule_var_map:
                self.rule_var_map[key] = ""
            # match TD one by one
            prev_depent = 0
            for tup in self.rule_TD_list:
                match_td_name = tup[0]
                var1_key = tup[1]
                var2_key = tup[2]
                flag = False
                aid = False # aid means that we should do dfs
                for val_tup in td_key[match_td_name]:
                    govnor = val_tup[0]
                    depent = val_tup[1]
                    if depent < prev_depent:
                        flag = False
                        continue

                    if self.rule_var_map[var1_key] == "":
                        self.rule_var_map[var1_key] = govnor
                    elif self.rule_var_map[var1_key] != govnor:
                        flag = False
                        aid = True
                        continue

                    if self.rule_var_map[var2_key] == "":
                        self.rule_var_map[var2_key] = depent
                    elif self.rule_var_map[var2_key] != depent:
                        flag = False
                        aid = True
                        continue

                    flag = True
                    prev_depent = depent
                    break

                if not flag:
                    break
                # TODO:
                # if aid:

            if not flag:
                line = file_obj.readline().strip()
                continue

            for key in self.rule_var_map:
                if self.rule_var_map[key] == "":
                    flag = False
                    break
            if not flag:
                line = file_obj.readline().strip()
                continue

            print "Matched: ", line
            for key in self.rule_var_map:
                print key, self.rule_var_map[key]

            line = file_obj.readline().strip()


if __name__ == '__main__':

    ssr = MatchSSR()
    # read rule
    rule_path = ssr.dir_path("/SSR/")
    rule_obj = ssr.read_one_file(rule_path, "SSR1.txt")
    ssr.parse_rule(rule_obj)
    rule_obj.close()
    # read sentences
    dir_path = ssr.dir_path("/Data/input_origin/")
    req_obj = ssr.read_one_file(dir_path, "test.txt")
    ssr.match(req_obj)
    req_obj.close()
