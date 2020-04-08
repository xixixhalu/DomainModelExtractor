import os
import pygtrie as trie
import json
from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *

class TransformationRules:

    class Operations:
        def __init__(self,name="",source="",dest="",para=""):
            self.name=name
            self.SourceEntityTerm=source
            self.DestEntityTerm=dest
            self.para=para


        def __str__(self):
            return "Name: "+str(self.name)+" Source1: "+str(self.SourceEntityTerm)+" Dest1: "+str(self.DestEntityTerm)+" Para: "+str(self.para)

        def __repr__(self):
            return "Name: "+str(self.name)+" Source1: "+str(self.SourceEntityTerm)+" Dest1: "+str(self.DestEntityTerm)+" Para: "+str(self.para)

    def __init__(self, file_path):
        self.file = open(file_path)
        self.class_dict = {}
        self.noun_trie = trie.CharTrie()
        self.noun_set = set()
        self.file_name = file_path.split("/")[-1]
        self.op_list =[]


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
            # word_list = []
            # pos_tags = parsePosTag(nlp_output)
            #
            # td_key = pure_enhancedTD(nlp_output)
            # for i in range(0, len(nlp_output['sentences'][0]['tokens']) ):
            #     word_list.append(nlp_output['sentences'][0]['tokens'][i]["word"])
            # self.tr4_initial(word_list,pos_tags)
            # self.tr5(word_list,td_key)
            # self.tr6(word_list,td_key)
            # self.tr7(word_list,td_key)
            # self.tr8(word_list,td_key)
            # self.tr9(word_list,td_key)
            line = self.file.readline().strip()
        # self.tr4()
        self.identifyClassOperations() #tr11-tr43
        # print "Classed with Attributes: "+str(self.class_dict)

    # TR4 is divided into 2 functions: tr4_initial(), tr4(). tr4_initial adds nouns into noun_trie(datatype: Trie).
    # This makes searching if one word starts with the other efficient as opposed to O(n^2) if we did a linear seach
    # for every word.
    def tr4_initial(self,wordlist,posTags):
        """
        POS-tags of each sentence in the UCS are scanned, and all the nouns are stored in a list named ListOfNouns.
        For every two nouns n1 and n2 in ListOfNouns
            If n2 startsWith n1 then
                class = createClass(A,"<<entity class>>"); class.addAttribute(B);
            EndIf
        EndFor
        """
        if "NN" in posTags:
            for tup in posTags["NN"]:
                if tup[0]==tup[1]:
                    self.noun_trie[wordlist[tup[0]-1]]=1
                    self.noun_set.add(wordlist[tup[0]-1])
        if "NP" in posTags:
            for tup in posTags["NP"]:
                if tup[0]==tup[1]:
                    self.noun_trie[wordlist[tup[0]-1]]=1
                    self.noun_set.add(wordlist[tup[0]-1])
        if "NNS" in posTags:
            for tup in posTags["NNS"]:
                if tup[0]==tup[1]:
                    self.noun_trie[wordlist[tup[0]-1]]=1
                    self.noun_set.add(wordlist[tup[0]-1])
        if "NNP" in posTags:
            for tup in posTags["NNP"]:
                if tup[0]==tup[1]:
                    self.noun_trie[wordlist[tup[0]-1]]=1
                    self.noun_set.add(wordlist[tup[0]-1])

    def tr4(self):
        for n in self.noun_set:
            n_list = self.noun_trie.items(prefix=n)
            if len(n_list)>1:
                for att,val in n_list:
                    if n!=att:
                        self.addToClassDict(n,att)



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
                            self.addToClassDict(word_list[nsubj_dependent-1],word_list[dobj_dependent-1] )

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
                self.addToClassDict(word_list[dependent-1],word_list[governor-1])
                a_dict[governor] = dependent
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
                self.addToClassDict(word_list[dependent-1],word_list[governor-1])
                a_dict[governor] = dependent
            # print a_dict
            for key in td_key:
                if "conj" in key:
                    val = td_key[key]
                    for li1,li2 in val:
                        if li1 in a_dict:
                            self.class_dict[word_list[a_dict[li1]-1]].append(word_list[li2-1])

    def tr8(self,word_list,td_key):
        """If TDs of the sentence contain TDs poss(A, B) then
                class = createClass(B,"<<entity class>>"); class.addAttribute(A);
           EndIf """
        if "nmod:poss" in td_key:
            for governor,dependent in td_key["nmod:poss"]:
                self.addToClassDict(word_list[dependent-1],word_list[governor-1])


    def tr9(self,word_list,td_key):
        """If TDs of the sentence contain TD amod(A, B) then
            class = createClass(A,"<<entity class>>"); class.addAttribute(B);
        EndIf """
        if "amod" in td_key:
            for governor,dependent in td_key["amod"]:
                self.addToClassDict(word_list[governor-1],word_list[dependent-1])

    def identifyClassOperations(self):
        # TODO: number to word conversion       
        op_list = []
        jsonFile = os.getcwd() + "/Data/output_origin/" + (self.file_name).split('.')[0] +"Result.json"
        with open(jsonFile) as f:
            data=json.load(f)

            def tr11():
                """
                SVIODO nsubj(A,B), iobj(A,C), dobj(A,D)
                op.SourceEntityTerm=B, op.DestEntityTerm=D, op.name=A                
                """
                for sentence in data["SVIODO"]:
                    td_dict = sentence[sentence.keys()[0]]["TD"]
                    if len(td_dict["nsubj"])==0:
                        print("Error in nsubj",sentence.keys()[0])
                    else:
                        a= ""
                        b= ""
                        d= ""
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if dobj_entry[0]==nsubj_entry[0]:
                                    for iobj_entry in td_dict["iobj"]:
                                        if iobj_entry[0]==dobj_entry[0]:
                                            a=nsubj_entry[0]
                                            b=nsubj_entry[1]
                                            d=dobj_entry[1]
                                            obj = self.Operations(name=a,source=b,dest=c)
                                            self.op_list.append(obj)

                

            def tr12():
                """ SVDOThatClause nsubj(A,B), dobj(A,C), mark(D,E), nsubj(D,F)
                     op.SourceEntityTerm=B, op.DestEntityTerm=C, op.name=A
                """
                for sentence in data["SVDOThatClause"]:
                    td_dict = sentence[sentence.keys()[0]]["TD"]
                    if len(td_dict["nsubj"])==0:
                        print("Error in nsubj",sentence.keys()[0])
                    else:
                        a= ""
                        b= ""
                        c= ""
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if dobj_entry[0]==nsubj_entry[0]:
                                    a = nsubj_entry[0]
                                    b = nsubj_entry[1]
                                    c = dobj_entry[1]
                                    obj = self.Operations(name=a,source=b,dest=c)
                                    self.op_list.append(obj)


            def tr13():
                """ SVThatClause: nsubj(A,B), mark(C,D), nsubj(C,E)
                op.SourceEntityTerm=B, op.DestEntityTerm=E, op.name=A
                """
                for sentence in data["SVThatClause"]:
                    td_dict = sentence[sentence.keys()[0]]["TD"]
                    if len(td_dict["nsubj"])<2 or len(td_dict["mark"])==0 :
                        print("Error in nsubj",sentence.keys()[0])
                    else:
                        a= ""
                        b= ""
                        e= ""
                        for nsubj2_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["mark"]:
                                if dobj_entry[0]==nsubj2_entry[0]:
                                    for nsubj1_entry in td_dict["nsubj"]:
                                        if nsubj1_entry[0]!=nsubj2_entry[0] and nsubj1_entry[1]!=nsubj2_entry[1]:
                                            a=nsubj1_entry[0]
                                            b=nsubj1_entry[1]
                                            e=nsubj2_entry[1]
                                            obj = self.Operations(name=a,source=b,dest=e)
                                            self.op_list.append(obj)

            

            def tr14():
                pass

            def tr15():
                pass

            def tr16():
                pass

            def tr17():
                """SVDOToInf: nsubj(A,B), dobj(A,C), mark(D,E), acl(C,D)
                op.SourceEntityTerm=B, op.DestEntityTerm=D, op.name=A
                If (TDs of the sentence contains TD dobj(D,F)) then
                op.SourceEntityTerm2=C,
                op.DestEntityTerm2=F,
                op.name2=D
                EndIf
                """
                for sentence in data["SVDOToInf"]:
                    td_dict = sentence[sentence.keys()[0]]["TD"]
                    if len(td_dict["nsubj"])<2 or len(td_dict["mark"])==0 :
                        print("Error in nsubj",sentence.keys()[0])
                    else:
                        a= ""
                        b= ""
                        d= ""
                        d_dict={}
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if dobj_entry[0]==nsubj_entry[0]:
                                    for acl_entry in td_dict["acl"]:
                                        if acl_entry[0]==dobj_entry[1]:
                                            for mark_entry in td_dict["mark"]:
                                                if mark_entry[0]==acl_entry[1]:
                                                    a=nsubj_entry[0]
                                                    b=nsubj_entry[1]
                                                    d=mark_entry[0]
                                                    obj=self.Operations(name=a,source=b,dest=d)
                                                    self.op_list.append(obj)
                                                    d_dict[d]=dobj_entry[1]
                        for dobj_entry in td_dict["dobj"]:
                            if dobj_entry[0] in d_dict:
                                obj = self.Operations(name=dobj_entry[0], source=d_dict[dobj_entry[0]], dest=dobj_entry[1])
                                self.op_list.append(obj)

            def tr18():
                """ 
                SVDOPresentPart: nsubj(A,B), dobj(A,C), partmod(C,D) dobj(D,E)
                op.SourceEntityTerm=B, op.DestEntityTerm=D, op.name=A
                If (TDs of the sentence contains TD dobj(D,E)) then
                op.DestEntityTerm.addAttribute(E)           
                For each TD=conj(X,Y) and (X==E) after dobj(D,E)
                destClass.addAttribute(Y)
                EndFor
                EndIf
                """
                #doubt in rule implementation

            def tr19():
                """ 
                SVDOPastPart: nsubj(A,B), dobj(A,C), acl(C,D)
                op.SourceEntityTerm=B, op.DestEntityTerm=C, op.name=A
                """
                for sentence in data["SVDOPastPart"]:
                    td_dict = sentence[sentence.keys()[0]]["TD"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["dobj"])==0 or len(td_dict["acl"])==0 :
                        print("Error in nsubj,dobj or acl ",sentence.keys()[0])
                    else:
                        a=""
                        b=""
                        c=""
                        print(sentence.keys()[0])
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if dobj_entry[0]==nsubj_entry[0]:
                                    for acl_entry in td_dict["acl"]:
                                        if acl_entry[0]==dobj_entry[1]:
                                            a = nsubj_entry[0]
                                            b = nsubj_entry[1]
                                            c = dobj_entry[1]
                                            obj=self.Operations(name=a,source=b,dest=c)
                                            self.op_list.append(obj)

            def tr20():
                pass

            def tr21():
                pass

            def tr22():
                pass

            def tr23():
                """ 
                SVDOConjClause: nsubj(A,B), dobj(A,C), advmod(D,E),nsubj(D,F)
                op.SourceEntityTerm=B, op.DestEntityTerm=C, op.name=A
                """
                #Did not search for adv and nsubj
                
                for sentence in data["SVDOConjClause"]:
                    td_dict = sentence[sentence.keys()[0]]["TD"]
                    if len(td_dict["nsubj"])<2 or len(td_dict["dobj"])==0 or len(td_dict["advmod"])==0 :
                        print("Error in nsubj,dobj or acl ",sentence.keys()[0])
                    else:
                        a=""
                        b=""
                        c=""
                        print(sentence.keys()[0])
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if nsubj_entry[0]==dobj_entry[0]:
                                    a=nsubj_entry[0]
                                    b=nsubj_entry[1]
                                    c=dobj_entry[1]
                                    obj=self.Operations(name=a,source=b,dest=c)
                                    self.op_list.append(obj)

            def tr24():
                """ 
                SVDOAdverbial: nsubj(A,B), dobj(A,C), advmod(A,D)
                op.SourceEntityTerm=B, op.DestEntityTerm=C, op.name=A
                """
                for sentence in data["SVDOAdverbial"]:
                    td_dict = sentence[sentence.keys()[0]]["TD"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["dobj"])==0 or len(td_dict["advmod"])==0 :
                        print("Error in nsubj,dobj or advmod ",sentence.keys()[0])
                    else:
                        a=""
                        b=""
                        c=""
                        print(sentence.keys()[0])
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if dobj_entry[0]==nsubj_entry[0]:
                                    for advmod_entry in td_dict["advmod"]:
                                        if advmod_entry[0]==dobj_entry[0]:
                                            a = nsubj_entry[0]
                                            b = nsubj_entry[1]
                                            c = dobj_entry[1]
                                            obj=self.Operations(name=a,source=b,dest=c)
                                            self.op_list.append(obj)


            def tr25():
                """
                SAuxVDO: nsubj(A,B), aux(A,C), dobj(A,D)
                op.SourceEntityTerm=B, op.DestEntityTerm=D, op.name=A
                """
                for sentence in data["SAuxVDO"]:
                    td_dict = sentence[sentence.keys()[0]]["TD"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["dobj"])==0 or len(td_dict["aux"])==0 :
                        print("Error in nsubj,dobj or aux ",sentence.keys()[0])
                    else:
                        a=""
                        b=""
                        d=""
                        print(sentence.keys()[0])
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if dobj_entry[0]==nsubj_entry[0]:
                                    for aux_entry in td_dict["aux"]:
                                        if aux_entry[0]==dobj_entry[0]:
                                            a = nsubj_entry[0]
                                            b = nsubj_entry[1]
                                            d = dobj_entry[1]
                                            obj=self.Operations(name=a,source=b,dest=d)
                                            self.op_list.append(obj)

            def tr26():
                """
                SVDOPO: nsubj(A,B), dobj(A,C), prep(A,D), pobj(D,E) [From the paper]
                        nsubj(A,B), dobj(A,C) [from the updated SSR list]
                op.SourceEntityTerm=B, op.name=A,
                If(E=='to' or 'from' or 'on' or 'in' or 'into' or 'through' or
                'of') then op.DestEntityTerm=E
                """  
                #discrepencies in paper and updated SSR(no E in updated SSR)

            def tr27():
                pass

            def tr28():
                """
                SVConjClause: nsubj(A,B), advmod(C,D), nsubj(C,E), advcl(A,C)
                op.SourceEntityTerm=B, op.DestEntityTerm=B, op.name=A
                """
                for sentence in data["SVConjClause"]:
                    td_dict = sentence[sentence.keys()[0]]["TD"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["advmod"])==0 or len(td_dict["advcl"])==0:
                        print("Error in nsubj,dobj or aux ",sentence.keys()[0])
                    else:
                        a=""
                        b=""
                        # d=""
                        print(sentence.keys()[0])
                        for nsubj_entry in td_dict["nsubj"]:
                            for advcl_entry in td_dict["advcl"]:
                                if nsubj_entry[0]==advcl_entry[0]:
                                    for advmod_entry in td_dict["advmod"]:
                                        if advmod_entry[0]==advcl_entry[1]:
                                            for nsubj_entry2 in td_dict["nsubj"]:
                                                if nsubj_entry!=nsubj_entry2 and nsubj_entry2[0]==advmod_entry[0]:
                                                    a=nsubj_entry[0]
                                                    b=nsubj_entry[1]
                                                    obj=self.Operations(name=a,source=b,dest=b)
                                                    self.op_list.append(obj)

            def tr29():
                """ 
                SVToInf: nsubj(A,B), mark(C,D), xcomp(A,C)
                op.SourceEntityTerm=B, op.name=A,
                If found(dobj(C,E)) then op.DestEntityTerm=E
                Else op.DestEntityTerm=B
                """
                for sentence in data["SVToInf"]:
                    td_dict = sentence[sentence.keys()[0]]["TD"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["mark"])==0 or len(td_dict["xcomp"])==0:
                        print("Error in nsubj,dobj or aux ",sentence.keys()[0])
                    else:
                        a=""
                        b=""
                        # d=""
                        print(sentence.keys()[0])
                        for nsubj_entry in td_dict["nsubj"]:
                            for xcomp_entry in td_dict["xcomp"]:
                                if nsubj_entry[0]==xcomp_entry[0]:
                                    for mark_entry in td_dict["mark"]:
                                        if mark_entry[0]==xcomp_entry[1]:
                                            a = nsubj_entry[0]
                                            b = nsubj_entry[1]
                                            dest = b
                                            for dobj_entry in td_dict["dobj"]:
                                                if dobj_entry[0]==mark_entry[0]:
                                                    dest=dobj_entry[1]
                                            obj=self.Operations(name=a,source=b,dest=dest)
                                            self.op_list.append(obj)

            def tr30():
                """
                SVGerund: nsubj(A,B), xcomp(A,C)
                op.SourceEntityTerm=B, op.name=A,
                If found(dobj(C,D)) then op.DestEntityTerm=D
                else op.DestEntityTerm=B
                """
                for sentence in data["SVGerund"]:
                    td_dict = sentence[sentence.keys()[0]]["TD"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["xcomp"])==0:
                        print("Error in nsubj,xcomp",sentence.keys()[0])
                    else:
                        a=""
                        b=""
                        print(sentence.keys()[0])
                        for nsubj_entry in td_dict["nsubj"]:
                            for xcomp_entry in td_dict["xcomp"]:
                                if nsubj_entry[0]==xcomp_entry[0]:                                
                                    a = nsubj_entry[0]
                                    b = nsubj_entry[1]
                                    dest = b
                                    for dobj_entry in td_dict["dobj"]:
                                        if dobj_entry[0]==xcomp_entry[1]:
                                            dest=dobj_entry[1]
                                    obj=self.Operations(name=a,source=b,dest=dest)
                                    self.op_list.append(obj)
            #function calls to inner functions
            tr11()
            # tr12()
            # tr13()
            # tr14()
            # tr15()
            # tr16()
            # tr17()
            # tr18()
            # tr19()
            # tr20()
            # tr21()
            # tr22()
            # tr23()
            # tr24()
            # tr25()
            # tr26()
            # tr27()
            # tr28()
            # tr29()
            # tr30()         
                                                    
            for item in self.op_list:
                print(item)


    def addToClassDict(self,className,attributeName):
        if className not in self.class_dict:
            self.class_dict[className]=[attributeName]
        else:
            self.class_dict[className].append([attributeName])


if __name__ == '__main__':
    p = TransformationRules(os.getcwd() + "/input/" + "2014-USC-Project02.txt")
    p.apply_rules()
