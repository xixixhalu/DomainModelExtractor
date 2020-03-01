import os
from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *

class TransformationRules:

    def __init__(self, file_path):
        self.file = open(file_path)
        self.class_dict = {}

    def apply_rules(self):
        line = self.file.readline().strip()
        while line:
            # print "Original sentence: ", line
            nlp_output = analyze(line)
            if nlp_output is None:
                print line, ": NLP API returns None. skip!"
                break
            elif nlp_output['sentences'] == []:
                break
            word_list = []
            td_key = pure_enhancedTD(nlp_output)
            for i in range(0, len(nlp_output['sentences'][0]['tokens']) ):
                word_list.append(nlp_output['sentences'][0]['tokens'][i]["word"])
            self.tr5(word_list,td_key)
            self.tr6(word_list,td_key)
            self.tr7(word_list,td_key)
            self.tr8(word_list,td_key)
            self.tr9(word_list,td_key)
            line = self.file.readline().strip()
        print "Classed with Attributes: "+str(self.class_dict)


    def tr5(self,word_list,td_key):
        """If TDs of the sentence contain TDs nsubj(has,A) and dobj(has, B) then
            class = createClass(A,"<<entity class>>"); class.addAttribute(B);
        EndIf """
        if "dobj" in td_key and "nsubj" in td_key:
            dobj_list = td_key["dobj"]
            nsubj_set = td_key["nsubj"]
            for nsubj_governor,nsubj_dependent in td_key["nsubj"]:
                if word_list[nsubj_governor-1] == "has":
                    for dobj_governor,dobj_dependent in td_key["dobj"]:
                        if nsubj_governor==dobj_governor:
                            self.class_dict[word_list[nsubj_dependent-1]] = [word_list[dobj_dependent-1]]

    def tr6(self, word_list,td_key):
        """If TDs of the sentence contain TDs prep(A,"on") and pobj("on",B) then
            class = createClass(B,"<<entity class>>"); class.addAttribute(A);
            For all consecutive TDs of type conj(A,C) before prep(A,"on")
                class.addAttribute(C);
            EndFor
            EndIf
        """
        # line = "The system prompts for the userName and password of the customer."
        a_dict = {}
        if "nmod:on" in td_key:
            for governor,dependent in td_key["nmod:on"]:
                if word_list[dependent-1] not in self.class_dict:
                    self.class_dict[word_list[dependent-1]] = [word_list[governor-1]]
                else:
                    self.class_dict[word_list[dependent-1]].append(word_list[governor-1])
                a_dict[governor] = dependent
            # print a_dict
            for key in td_key:
                if "conj" in key:
                    val = td_key[key]
                    for li1,li2 in val:
                        if li1 in a_dict:
                            self.class_dict[word_list[a_dict[li1]-1]].append(word_list[li2-1])


    def tr7(self, word_list,td_key):
        """If TDs of the sentence contain TDs prep(A,"of") and pobj("of",B) then
            class = createClass(B,"<<entity class>>"); class.addAttribute(A);
            For all consecutive TDs of type conj(A,C) before prep(A,"in")
                class.addAttribute(C);
            EndFor
            EndIf
        """
        # line = "The system prompts for the userName and password of the customer."
        a_dict = {}
        if "nmod:of" in td_key:
            for governor,dependent in td_key["nmod:of"]:
                if word_list[dependent-1] not in self.class_dict:
                    self.class_dict[word_list[dependent-1]] = [word_list[governor-1]]
                else:
                    self.class_dict[word_list[dependent-1]].append(word_list[governor-1])
                a_dict[governor] = dependent
            # print a_dict
            for key in td_key:
                if "conj" in key:
                    val = td_key[key]
                    for li1,li2 in val:
                        if li1 in a_dict:
                            self.class_dict[word_list[a_dict[li1]-1]].append(word_list[li2-1])
        # print str(self.class_dict)

    def tr8(self,word_list,td_key):
        """If TDs of the sentence contain TDs poss(A, B) then
                class = createClass(B,"<<entity class>>"); class.addAttribute(A);
           EndIf """
        if "nmod:poss" in td_key:
            # print td_key["nmod:poss"]
            for governor,dependent in td_key["nmod:poss"]:
                if word_list[dependent-1] not in self.class_dict:
                    self.class_dict[word_list[dependent-1]] = [word_list[governor-1]]
                else:
                    self.class_dict[word_list[dependent-1]].append(word_list[governor-1])
        # print str(self.class_dict)


    def tr9(self,word_list,td_key):
        """If TDs of the sentence contain TD amod(A, B) then
            class = createClass(A,"<<entity class>>"); class.addAttribute(B);
        EndIf """
        if "amod" in td_key:
            for governor,dependent in td_key["amod"]:
                if word_list[governor-1] not in self.class_dict:
                    self.class_dict[word_list[governor-1]] = [word_list[dependent-1]]
                else:
                    self.class_dict[word_list[governor-1]].append(word_list[dependent-1])


if __name__ == '__main__':
    p = TransformationRules(os.getcwd() + "/input/" + "2014-USC-Project02.txt")
    # p = PreProcessor(os.getcwd() + "/Data/input_origin/" + "test.txt")
    p.apply_rules()
