import os
import pygtrie as trie
import json
from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *

class TransformationRules:

    class Operations:
        def __init__(self,name="",source="",dest="",para="",sentence=""):
            self.name=name
            self.SourceEntityTerm=source
            self.DestEntityTerm=dest
            self.para=para
            self.sentence=sentence


        def __str__(self):
            return "Name: "+str(self.name)+" Source1: "+str(self.SourceEntityTerm)+" Dest1: "+str(self.DestEntityTerm)+" Para: "+str(self.para)+"\nSentence: "+self.sentence

        def __repr__(self):
            return "Name: "+str(self.name)+" Source1: "+str(self.SourceEntityTerm)+" Dest1: "+str(self.DestEntityTerm)+" Para: "+str(self.para)+"\nSentence: "+self.sentence

    def __init__(self, file_path):
        self.file = open(file_path)
        self.class_dict = {}
        self.noun_trie = trie.CharTrie()
        self.noun_set = set()
        self.file_name = file_path.split("/")[-1]
        self.op_list =[]
        self.relationship_dict = {}


    def apply_rules(self):
        line = self.file.readline().strip()
        while line:
            #print( "Original sentence: ", line)
            nlp_output = analyze(line)
            if nlp_output is None:
                print (line, ": NLP API returns None. skip!")
                break
            elif nlp_output['sentences'] == []:
                break
            word_list = []
            pos_tags = parsePosTag(nlp_output)            
            td_key = pure_enhancedTD(nlp_output)
            for i in range(0, len(nlp_output['sentences'][0]['tokens']) ):
                word_list.append(nlp_output['sentences'][0]['tokens'][i]["word"])
            self.tr4_initial(word_list,pos_tags)
            self.tr5(word_list,td_key)
            self.tr6(word_list,td_key)
            self.tr7(word_list,td_key)
            self.tr8(word_list,td_key)
            self.tr9(word_list,td_key)
            
            lemma_list = []
            for i in range(0, len(nlp_output['sentences'][0]['tokens']) ):
                lemma_list.append(nlp_output['sentences'][0]['tokens'][i]["lemma"])
            self.tr52(lemma_list,pos_tags)
            self.tr53(lemma_list,pos_tags)
            
            line = self.file.readline().strip()
        self.tr4()
        #TR11-TR43
        self.identifyClassOperations()
        self.tr44()
        self.tr45()
        #self.tr46()
        
        self.tr51()
        self.tr54()
        
        print ("Classed with Attributes: "+str(self.class_dict))
        print ("Relationships with parent class & child class: "+str(self.relationship_dict))

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
                        #self.addToClassDict(n,att)
                        self.addAttributeToClass(n, att)



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
                            #self.addToClassDict(word_list[nsubj_dependent-1],word_list[dobj_dependent-1] )
                            self.addAttributeToClass(word_list[nsubj_dependent-1],word_list[dobj_dependent-1])

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
                #self.addToClassDict(word_list[dependent-1],word_list[governor-1])
                self.addAttributeToClass(word_list[dependent-1],word_list[governor-1])
                a_dict[governor] = dependent
            for key in td_key:
                if "conj" in key:
                    val = td_key[key]
                    for li1,li2 in val:
                        if li1 in a_dict:
                            #self.class_dict[word_list[a_dict[li1]-1]].append(word_list[li2-1])
                            self.addAttributeToClass(word_list[a_dict[li1]-1], word_list[li2-1])
                            


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
                #self.addToClassDict(word_list[dependent-1],word_list[governor-1])
                self.addAttributeToClass(word_list[dependent-1],word_list[governor-1])
                a_dict[governor] = dependent
            # print a_dict
            for key in td_key:
                if "conj" in key:
                    val = td_key[key]
                    for li1,li2 in val:
                        if li1 in a_dict:
                            #self.class_dict[word_list[a_dict[li1]-1]].append(word_list[li2-1])
                            self.addAttributeToClass(word_list[a_dict[li1]-1], word_list[li2-1])

    def tr8(self,word_list,td_key):
        """If TDs of the sentence contain TDs poss(A, B) then
                class = createClass(B,"<<entity class>>"); class.addAttribute(A);
           EndIf """
        if "nmod:poss" in td_key:
            for governor,dependent in td_key["nmod:poss"]:
                #self.addToClassDict(word_list[dependent-1],word_list[governor-1])
                self.addAttributeToClass(word_list[dependent-1],word_list[governor-1])


    def tr9(self,word_list,td_key):
        """If TDs of the sentence contain TD amod(A, B) then
            class = createClass(A,"<<entity class>>"); class.addAttribute(B);
        EndIf """
        if "amod" in td_key:
            for governor,dependent in td_key["amod"]:
                #self.addToClassDict(word_list[governor-1],word_list[dependent-1])
                self.addAttributeToClass(word_list[governor-1],word_list[dependent-1])

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
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["dobj"])==0 :
                        print("Error in nsubj or dobj",list(sentence.keys())[0])
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
                                            obj = self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(d)],sentence=list(sentence.keys())[0])
                                            self.op_list.append(obj)

                

            def tr12():
                """ SVDOThatClause nsubj(A,B), dobj(A,C), mark(D,E), nsubj(D,F)
                     op.SourceEntityTerm=B, op.DestEntityTerm=C, op.name=A
                """
                for sentence in data["SVDOThatClause"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["dobj"])==0:
                        print("Error in nsubj or dobj",list(sentence.keys())[0])
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
                                    # print(a,b,c)
                                    obj = self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(c)],sentence=list(sentence.keys())[0])
                                    self.op_list.append(obj)


            def tr13():
                """ SVThatClause: nsubj(A,B), mark(C,D), nsubj(C,E)
                op.SourceEntityTerm=B, op.DestEntityTerm=E, op.name=A
                """
                for sentence in data["SVThatClause"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])<2 or len(td_dict["mark"])==0 :
                        print("Error in nsubj",list(sentence.keys())[0])
                    else:
                        a= ""
                        b= ""
                        e= ""
                        for nsubj2_entry in td_dict["nsubj"]:
                            for mark_entry in td_dict["mark"]:
                                if mark_entry[0]==nsubj2_entry[0]:
                                    for nsubj1_entry in td_dict["nsubj"]:
                                        if nsubj1_entry[0]!=nsubj2_entry[0] and nsubj1_entry[1]!=nsubj2_entry[1]:
                                            a=nsubj1_entry[0]
                                            b=nsubj1_entry[1]
                                            e=nsubj2_entry[1]
                                            obj = self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(e)],sentence=list(sentence.keys())[0])
                                            self.op_list.append(obj)

            

            def tr14():
                """
                SVDONotToInf: nsubj(A,B), dobj(A,C), neg(D,E), mark(D,F), acl(C,D)
                op.SourceEntityTerm=B, op.DestEntityTerm=C, op.name=A
                """
                for sentence in data["SVDONotToInf"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["dobj"])==0 or len(td_dict["neg"])==0 or len(td_dict["mark"])==0 or len(td_dict["acl"])==0:
                        print("Error in nsubj",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        c=""
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if nsubj_entry[0]==dobj_entry[0]:
                                    for acl_entry in td_dict["acl"]:
                                        if dobj_entry[1]==acl_entry[0]:
                                            for mark_entry in td_dict["mark"]:
                                                if acl_entry[1]==mark_entry[0]:
                                                    for neg_entry in td_dict["neg"]:
                                                        if mark_entry[1]==neg_entry[0]:
                                    
                                                           a=nsubj_entry[0]
                                                           b=nsubj_entry[1]
                                                           c=dobj_entry[1]
                                                           obj = self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(c)],sentence=list(sentence.keys())[0])
                                                           self.op_list.append(obj)
                

            def tr15():
                """
                SVNotToInf: nsubj(A,B), neg(D,E), mark(C,E), xcomp(A,C), dobj(C,F)
                op.SourceEntityTerm=B, op.DestEntityTerm=F, op.name=A
                """
                for sentence in data["SVNotToInf"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["xcomp"])==0 or len(td_dict["dobj"])==0 or len(td_dict["neg"])==0 or len(td_dict["mark"])==0:
                        print("Error in nsubj",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        f=""
                        for nsubj_entry in td_dict["nsubj"]:
                            for xcomp_entry in td_dict["xcomp"]:
                                if nsubj_entry[0]==xcomp_entry[0]:
                                    for dobj_entry in td_dict["dobj"]:
                                        if dobj_entry[0]==xcomp_entry[1]:
                                            for neg_entry in td_dict["neg"]:
                                                if neg_entry[0]==dobj_entry[0]:
                                                    for mark_entry in td_dict["mark"]:
                                                        if mark_entry[0]==neg_entry[0]:
                                                            a=nsubj_entry[0]
                                                            b=nsubj_entry[1]
                                                            f=dobj_entry[0]
                                                            obj = self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(f)],sentence=list(sentence.keys())[0])
                                                            self.op_list.append(obj)
                        
                        
            def tr16():
                """
                SVDOtobeComp:nsubj(A,B), nsubj(C,D), mark(C,E), cop(C,F), xcomp(A,C)
                op.SourceEntityTerm=B, op.DestEntityTerm=D, op.name=A
                """
                for sentence in data["SVDOtobeComp"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])<2 or len(td_dict["mark"])==0 or len(td_dict["cop"])==0 or len(td_dict["xcomp"])==0:
                        print("Error in nsubj",list(sentence.keys())[0])
                    else:
                        a= ""
                        b= ""
                        d= ""
                        for nsubj2_entry in td_dict["nsubj"]:
                            for nsubj1_entry in td_dict["nsubj"]:
                                if nsubj1_entry[0]!=nsubj2_entry[0] and nsubj1_entry[1]!=nsubj2_entry[1]:
                                    for xcomp_entry in td_dict["xcomp"]:
                                        if nsubj1_entry[0]==xcomp_entry[0] and nsubj2_entry[0]==xcomp_entry[1]:
                                            for mark_entry in td_dict["mark"]:
                                                if mark_entry[0]==xcomp_entry[1]:
                                                    for cop_entry in td_dict["cop"]:
                                                        if cop_entry[0]==mark_entry[0]:
                                                            
                                            
                                                            a=nsubj1_entry[0]
                                                            b=nsubj1_entry[1]
                                                            d=nsubj2_entry[1]
                                                            obj = self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(d)],sentence=list(sentence.keys())[0])
                                                            self.op_list.append(obj)

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
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])<2 or len(td_dict["mark"])==0 :
                        print("Error in nsubj",list(sentence.keys())[0])
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
                                                    obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(d)],sentence=list(sentence.keys())[0])
                                                    self.op_list.append(obj)
                                                    d_dict[d]=dobj_entry[1]
                        for dobj_entry in td_dict["dobj"]:
                            if dobj_entry[0] in d_dict:
                                obj = self.Operations(name=index_dict[str(dobj_entry[0])], source=index_dict[str(d_dict[dobj_entry[0]])], dest=index_dict[str(dobj_entry[1])],sentence=list(sentence.keys())[0])
                                self.op_list.append(obj)

            def tr18():
                """ ****************
                SVDOPresentPart: nsubj(A,B), dobj(A,C), partmod(C,D), POS-tag(D)==“VBG”
                op.SourceEntityTerm=B, op.DestEntityTerm=D, op.name=A
                If (TDs of the sentence contains TD dobj(D,E)) then
                op.DestEntityTerm.addAttribute(E)           
                For each TD=conj(X,Y) and (X==E) after dobj(D,E)
                destClass.addAttribute(Y)
                EndFor
                EndIf
                """
                """
                #doubt in rule implementation
                for sentence in data["SVDOPresentPart"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["dobj"])==0 or len(td_dict["partmod"])==0 :
                        print("Error in nsubj",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        d=""
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if nsubj_entry[0]==dobj_entry[0]:
                                    for partmod_entry in td_dict["partmod"]:
                                        if partmod_entry[0]==dobj_entry[1]:
                                            for dobj_entry in td_dict["dobj"]:
                                                if dobj_entry[0]==partmod_entry[1]:
                                                    a=nsubj_entry[0]
                                                    b=nsubj_entry[1]
                                                    d=mark_entry[0]
                                                    obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(d)],sentence=list(sentence.keys())[0])
                                                    self.op_list.append(obj)
                                                    """
                pass 
                                                    

            def tr19():
                """ 
                SVDOPastPart: nsubj(A,B), dobj(A,C), acl(C,D)
                op.SourceEntityTerm=B, op.DestEntityTerm=C, op.name=A
                """
                for sentence in data["SVDOPastPart"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["dobj"])==0 or len(td_dict["acl"])==0 :
                        print("Error in nsubj,dobj or acl ",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        c=""
                        # print(list(sentence.keys())[0])
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if dobj_entry[0]==nsubj_entry[0]:
                                    for acl_entry in td_dict["acl"]:
                                        if acl_entry[0]==dobj_entry[1]:
                                            a = nsubj_entry[0]
                                            b = nsubj_entry[1]
                                            c = dobj_entry[1]
                                            obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(c)],sentence=list(sentence.keys())[0])
                                            self.op_list.append(obj)

            def tr20():
                """
                SVDOAdj:nsubj(A,B), nsubj(C,D), xcomp(A,C)
                op.SourceEntityTerm=B, op.DestEntityTerm=D, op.name=A
                """
                for sentence in data["SVDOAdj"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])<2 or len(td_dict["xcomp"])==0 :
                        print("Error in nsubj, or xcomp",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        d=""
                        for nsubj1_entry in td_dict["nsubj"]:
                            for xcomp_entry in td_dict["xcomp"]:
                                if nsubj1_entry[0]==xcomp_entry[0]:
                                    for nsubj2_entry in td_dict["nsubj"]:
                                        if nsubj1_entry!=nsubj2_entry and nsubj2_entry[0]==xcomp_entry[1]:
                                            a=nsubj1_entry[0]
                                            b=nsubj1_entry[1]
                                            d=nsubj2_entry[1]
                                            obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(d)],sentence=list(sentence.keys())[0])
                                            self.op_list.append(obj)
                                                                    
                        

            def tr21():
                """
                SVDONoun:nsubj(A,B), nsubj(C,D), xcomp(A,C)
                op.SourceEntityTerm=B, op.DestEntityTerm=D, op.name=A
                """
                for sentence in data["SVDONoun"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])<2 or len(td_dict["xcomp"])==0 :
                        print("Error in nsubj, or xcomp",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        d=""
                        for nsubj1_entry in td_dict["nsubj"]:
                            for xcomp_entry in td_dict["xcomp"]:
                                if nsubj1_entry[0]==xcomp_entry[0]:
                                    for nsubj2_entry in td_dict["nsubj"]:
                                        if nsubj1_entry!=nsubj2_entry and nsubj2_entry[0]==xcomp_entry[1]:
                                            a=nsubj1_entry[0]
                                            b=nsubj1_entry[1]
                                            d=nsubj2_entry[1]
                                            obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(d)],sentence=list(sentence.keys())[0])
                                            self.op_list.append(obj)
                        

            def tr22():
                """
                SVDOConjToInf:nsubj(A,B), dobj(A,C), advmod(D,E), mark(D,F), xcomp(A,D)
                op.SourceEntityTerm=B, op.DestEntityTerm=C, op.name=A
                """
                for sentence in data["SVDOConjToInf"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["dobj"])==0 or len(td_dict["advmod"])==0 or len(td_dict["aux"])==0 or len(td_dict["xcomp"]==0):
                        
                        print("Error in nsubj or dobj",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        c=""
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if nsubj_entry[0]==dobj_entry[0]:
                                    for xcomp_entry in td_dict["xcomp"]:
                                        if xcomp_entry[0]==nsubj_entry[0]:
                                            for advmod_entry in td_dict["advmod"]:
                                                if advmod_entry[0]==xcomp_entry[1]:
                                                    for mark_entry in td_dict["mark"]:
                                                        if mark_entry[0]==advmod_entry[0]:
                                                            
                                                            a=nsubj_entry[0]
                                                            b=nsubj_entry[1]
                                                            c=dobj_entry[1]
                                                            obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(c)],sentence=list(sentence.keys())[0])
                                                            self.op_list.append(obj)
                

            def tr23():
                """ 
                SVDOConjClause: nsubj(A,B), dobj(A,C), advmod(D,E),nsubj(D,F)
                op.SourceEntityTerm=B, op.DestEntityTerm=C, op.name=A
                """
                #Did not search for adv and nsubj
                
                for sentence in data["SVDOConjClause"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])<2 or len(td_dict["dobj"])==0 or len(td_dict["advmod"])==0 :
                        print("Error in nsubj,dobj or acl ",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        c=""
                        # print(list(sentence.keys())[0])
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if nsubj_entry[0]==dobj_entry[0]:
                                    a=nsubj_entry[0]
                                    b=nsubj_entry[1]
                                    c=dobj_entry[1]
                                    obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(c)],sentence=list(sentence.keys())[0])
                                    self.op_list.append(obj)

            def tr24():
                """ 
                SVDOAdverbial: nsubj(A,B), dobj(A,C), advmod(A,D)
                op.SourceEntityTerm=B, op.DestEntityTerm=C, op.name=A
                """
                for sentence in data["SVDOAdverbial"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["dobj"])==0 or len(td_dict["advmod"])==0 :
                        print("Error in nsubj,dobj or advmod ",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        c=""
                        # print(list(sentence.keys())[0])
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if dobj_entry[0]==nsubj_entry[0]:
                                    for advmod_entry in td_dict["advmod"]:
                                        if advmod_entry[0]==dobj_entry[0]:
                                            a = nsubj_entry[0]
                                            b = nsubj_entry[1]
                                            c = dobj_entry[1]
                                            obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(c)],sentence=list(sentence.keys())[0])
                                            self.op_list.append(obj)


            def tr25():
                """
                SAuxVDO: nsubj(A,B), aux(A,C), dobj(A,D)
                op.SourceEntityTerm=B, op.DestEntityTerm=D, op.name=A
                """
                for sentence in data["SAuxVDO"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["dobj"])==0 or len(td_dict["aux"])==0 :
                        print("Error in nsubj,dobj or aux ",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        d=""
                        # print(list(sentence.keys())[0])
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if dobj_entry[0]==nsubj_entry[0]:
                                    for aux_entry in td_dict["aux"]:
                                        if aux_entry[0]==dobj_entry[0]:
                                            a = nsubj_entry[0]
                                            b = nsubj_entry[1]
                                            d = dobj_entry[1]
                                            obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(d)],sentence=list(sentence.keys())[0])
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
                """
                SVConjToInf: nsubj(A,B), advmod(C,D), aux(C,E), xcomp(A,C)
                op.SourceEntityTerm=B, op.DestEntityTerm=B, op.name=A
                """
                for sentence in data["SVConjToInf"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["advmod"])==0 or len(td_dict["aux"])==0 or len(td_dict["xcomp"])==0:
                        print("Error in nsubj",list(sentence.keys())[0])
                    else:
                        a=""
                        b_s=""
                        b_d=""
                        for nsubj_entry in td_dict["nsubj"]:
                            for xcomp_entry in td_dict["xcomp"]:
                                if nsubj_entry[0]==xcomp_entry[0]:
                                    for advmod_entry in td_dict["advmod"]:
                                        if advmod_entry[0]==xcomp_entry[1]:
                                            for aux_entry in td_dict["aux"]:
                                                if aux_entry[0]==advmod_entry[0]:
                                            
                                                   a = nsubj_entry[0]
                                                   b_s = nsubj_entry[1]
                                                   b_d = nsubj_entry[1]
                                                   obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b_s)],dest=index_dict[str(b_d)],sentence=list(sentence.keys())[0])
                                                   self.op_list.append(obj)
                

            def tr28():
                """
                SVConjClause: nsubj(A,B), advmod(C,D), nsubj(C,E), advcl(A,C)
                op.SourceEntityTerm=B, op.DestEntityTerm=B, op.name=A
                """
                for sentence in data["SVConjClause"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["advmod"])==0 or len(td_dict["advcl"])==0:
                        print("Error in nsubj,dobj or aux ",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        # d=""
                        # print(list(sentence.keys())[0])
                        for nsubj_entry in td_dict["nsubj"]:
                            for advcl_entry in td_dict["advcl"]:
                                if nsubj_entry[0]==advcl_entry[0]:
                                    for advmod_entry in td_dict["advmod"]:
                                        if advmod_entry[0]==advcl_entry[1]:
                                            for nsubj_entry2 in td_dict["nsubj"]:
                                                if nsubj_entry!=nsubj_entry2 and nsubj_entry2[0]==advmod_entry[0]:
                                                    a=nsubj_entry[0]
                                                    b=nsubj_entry[1]
                                                    obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(b)],sentence=list(sentence.keys())[0])
                                                    self.op_list.append(obj)

            def tr29():
                """ 
                SVToInf: nsubj(A,B), mark(C,D), xcomp(A,C)
                op.SourceEntityTerm=B, op.name=A,
                If found(dobj(C,E)) then op.DestEntityTerm=E
                Else op.DestEntityTerm=B
                """
                for sentence in data["SVToInf"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["mark"])==0 or len(td_dict["xcomp"])==0:
                        print("Error in nsubj,dobj or aux ",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        # d=""
                        # print(list(sentence.keys())[0])
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
                                            obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(dest)],sentence=list(sentence.keys())[0])
                                            self.op_list.append(obj)

            def tr30():
                """
                SVGerund: nsubj(A,B), xcomp(A,C)
                op.SourceEntityTerm=B, op.name=A,
                If found(dobj(C,D)) then op.DestEntityTerm=D
                else op.DestEntityTerm=B
                """
                for sentence in data["SVGerund"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["xcomp"])==0:
                        print("Error in nsubj,xcomp",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        # print(list(sentence.keys())[0])
                        for nsubj_entry in td_dict["nsubj"]:
                            for xcomp_entry in td_dict["xcomp"]:
                                if nsubj_entry[0]==xcomp_entry[0]:                                
                                    a = nsubj_entry[0]
                                    b = nsubj_entry[1]
                                    dest = b
                                    for dobj_entry in td_dict["dobj"]:
                                        if dobj_entry[0]==xcomp_entry[1]:
                                            dest=dobj_entry[1]
                                    obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(dest)],sentence=list(sentence.keys())[0])
                                    self.op_list.append(obj)
                
            def tr31():
                """
                SVAdverbialAdjunct: nsubj(A,B), advmod(A,C)
                op.SourceEntityTerm=B, op.DestEntityTerm=B, op.name=A
                """
                for sentence in data["SVAdverbialAdjunct"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["advmod"])==0:
                        print("Error in nsubj,advmod",list(sentence.keys())[0])
                    else:
                        a=""
                        b="" 
                        for nsubj_entry in td_dict["nsubj"]:
                            for advmod_entry in td_dict["advmod"]:
                                if nsubj_entry[0]==advmod_entry[0]:
                                    a = nsubj_entry[0]
                                    b = nsubj_entry[1]
                                    obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(b)],sentence=list(sentence.keys())[0])
                                    self.op_list.append(obj)

            def tr32():
                """
                SVPredicative: nsubj(A,B), cop(A,C)
                If(isAdjective(C)) then B.addAttribute(C)
                else if(isNoun(C)) then parentClass=C, childClass=B createRelationship(parentClass, childClass, “generalization”)
                """
                """
                The customer is employee
                nsubj(employee-4, customer-2)  cop(employee-4, is-3)
                isAdjective(C)==>isAdjective(A)
                isNoun(C)==>isNoun(A)
                """
                #doubt in implementation 
                for sentence in data["SVPredicative"]:
                    #print("*******************")
                    #print(sentence.keys())
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    #print(index_dict)
                    
                    if "ADJP" in sentence[list(sentence.keys())[0]]["Pos-tag"]:
                        adj_list = sentence[list(sentence.keys())[0]]["Pos-tag"]["ADJP"]
                    else:
                        adj_list=[]
                    
                    noun_list = []
                    if "NN" in sentence[list(sentence.keys())[0]]["Pos-tag"]:
                        noun_list = noun_list + sentence[list(sentence.keys())[0]]["Pos-tag"]["NN"]
                    if "NNS" in sentence[list(sentence.keys())[0]]["Pos-tag"]:
                        noun_list = noun_list + sentence[list(sentence.keys())[0]]["Pos-tag"]["NNS"]
                    if "NNP" in sentence[list(sentence.keys())[0]]["Pos-tag"]:
                        noun_list = noun_list + sentence[list(sentence.keys())[0]]["Pos-tag"]["NNP"]
                    if "NNPS" in sentence[list(sentence.keys())[0]]["Pos-tag"]:
                        noun_list = noun_list + sentence[list(sentence.keys())[0]]["Pos-tag"]["NNPS"]
                    # if "NP" in sentence[list(sentence.keys())[0]]["Pos-tag"]:
                    #     noun_list = noun_list + sentence[list(sentence.keys())[0]]["Pos-tag"]["NP"]
                    
                    #print(type(adj_list[0][0]))
                    #print(noun_list)
                    if len(td_dict["nsubj"])==0 or len(td_dict["cop"])==0:
                        print("Error in nsubj,cop",list(sentence.keys())[0])
                    else:
                        a="" #employee
                        b="" #customer
                        c="" #is
                        #print(td_dict["nsubj"])
                        #print(td_dict["cop"])
                        for nsubj_entry in td_dict["nsubj"]:
                            for cop_entry in td_dict["cop"]:
                                if nsubj_entry[0]==cop_entry[0]:
                                    #print("find match.....")
                                    a=nsubj_entry[0]
                                    b=nsubj_entry[1]
                                    c=cop_entry[1]
                                    #print(noun_list)
                                    #print(a,index_dict[str(a)])
                                    #print(index_dict[str(a)])
                                    for start, end in adj_list:
                                        if a>=start and a<=end:
                                            #self.addToClassDict(index_dict[str(b)],index_dict[str(c)])
                                            self.addAttributeToClass(index_dict[str(b)],index_dict[str(c)])
                                            break
                                    for start, end in noun_list:
                                        if a>=start and a<=end:
                                            self.addToRelationshipDict(index_dict[str(c)],index_dict[str(b)],[],"generalization")
                                            break
                                    # if [a,a] in adj_list:
                                    #     #print("adj find...........")
                                    #     self.addToClassDict(index_dict[str(b)],index_dict[str(a)])
                                    # elif [a,a] in noun_list:
                                    #     #print("noun find...........")
                                    #     self.addToRelationshipDict(index_dict[str(a)],index_dict[str(b)],"generalization")
                                    
                
            def tr33():
                """
                SVForComp: nsubj(A,B), nummod(D,E), case(D,C)
                op.SourceEntityTerm=B, op.name=A,
                If(A==E) then op.DestEntityTerm=B
                else op.DestEntityTerm=E
                """
                #doubt in implementation
                for sentence in data["SVForComp"]:
                    
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["nummod"])==0 or len(td_dict["case"])==0:
                        print("Error in nsubj,advmod",list(sentence.keys())[0])
                    else:
                         a="" 
                         b=""
                         c="" 
                         for nsubj_entry in td_dict["nsubj"]:
                           for nummod_entry in td_dict["nummod"]:
                             for case_entry in td_dict["case"]:
                                 if nummod_entry[0]==case_entry[0]:
                                     a=nsubj_entry[0]
                                     b=nsubj_entry[1]
                                     if nsubj_entry[0]==nummod_entry[1] :
                                          c=nsubj_entry[1]
                                     else:
                                          c=nummod_entry[1]
                                     obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(c)],sentence=list(sentence.keys())[0])
                                     self.op_list.append(obj)   
            
            def tr34():
                """
                SVPassPO: nsubjpass(A,B), auxpass(A,C), case(E,D)
                op.SourceEntityTerm=E, op.DestEntityTerm=B, op.name=A
                """
                #doubt in implementation
                for sentence in data["SVPassPO"]:
                    #print(sentence.keys(),'a')
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubjpass"])==0 or len(td_dict["auxpass"])==0 or len(td_dict["case"])==0:
                        print("Error in nsubj,dobj",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        e=""
                        for nsubjpass_entry in td_dict["nsubjpass"]:
                            for auxpass_entry in td_dict["auxpass"]:
                                for case_entry in td_dict["case"]:
                                  if nsubjpass_entry[0]==auxpass_entry[0]:
                                    a=nsubjpass_entry[0]
                                    b=nsubjpass_entry[1]
                                    e=case_entry[0]
                                    obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(e)],sentence=list(sentence.keys())[0])
                                    self.op_list.append(obj)
            def tr35():
                """
                SAuxVPassPO: nsubjpass(A,B), aux(A,C), auxpass(A,D), case(F,E)
                op.SourceEntityTerm=F, op.DestEntityTerm=B, op.name=A
                """
                #doubt in implementation
                for sentence in data["SAuxVPassPO"]:
                    #print(sentence.keys(),'a')
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubjpass"])==0 or len(td_dict["auxpass"])==0 or len(td_dict["case"])==0 or len(td_dict["aux"])==0:
                        print("Error in nsubj,dobj",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        f=""
                        for nsubjpass_entry in td_dict["nsubjpass"]:
                            for auxpass_entry in td_dict["auxpass"]:
                                for aux_entry in td_dict["aux"]:
                                    for case_entry in td_dict["case"]:
                                      if nsubjpass_entry[0]==aux_entry[0] and nsubjpass_entry[0]==auxpass_entry[0]:
                                          a=nsubjpass_entry[0]
                                          b=nsubjpass_entry[1]
                                          f=case_entry[0]
                                          obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(f)],sentence=list(sentence.keys())[0])
                                          self.op_list.append(obj)
            def tr36():
                """
                SVPO: nsubj(A,B), pobj(A,C)
                op.SourceEntityTerm=B, op.DestEntityTerm=C, op.name=A
                """
                #doubt in implementation
                for sentence in data["SVPO"]:
                    #print(sentence.keys(),'a')
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["case"])==0 :
                        print("Error in nsubj,dobj",list(sentence.keys())[0])
                    else  :
                        a=""
                        b=""
                        c=""
                        for nsubj_entry in td_dict["nsubj"]:
                            for case_entry in td_dict["case"]:
                                if nsubj_entry[0]==case_entry[0]:
                                    a=nsubj_entry[0]
                                    b=nsubj_entry[1]
                                    c=case_entry[1]
                                    obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(c)],sentence=list(sentence.keys())[0])
                                    self.op_list.append(obj)
            def tr37():
                """
                SVDO: nsubj(A,B), dobj(A,C)
                op.SourceEntityTerm=B, op.DestEntityTerm=C, op.name=A
                """
                for sentence in data["SVDO"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0 or len(td_dict["dobj"])==0:
                        print("Error in nsubj,dobj",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        c=""
                        for nsubj_entry in td_dict["nsubj"]:
                            for dobj_entry in td_dict["dobj"]:
                                if nsubj_entry[0]==dobj_entry[0]:
                                    a = nsubj_entry[0]
                                    b = nsubj_entry[1]
                                    c = dobj_entry[1]
                                    obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(c)],sentence=list(sentence.keys())[0])
                                    self.op_list.append(obj)

            def tr38():
                """
                Conditional: mark(A,B)
                """
                #doubt in implementation
                pass

            def tr39():
                """
                SV: nsubj(A,B)
                op.SourceEntityTerm=B, op.name=A, op.Para="", op.DestEntityTerm=B
                """
                for sentence in data["SV"]:
                    td_dict = sentence[list(sentence.keys())[0]]["TD"]
                    index_dict = sentence[list(sentence.keys())[0]]["Index"]
                    if len(td_dict["nsubj"])==0:
                        print("Error in nsubj",list(sentence.keys())[0])
                    else:
                        a=""
                        b=""
                        for nsubj_entry in td_dict["nsubj"]:
                            a = nsubj_entry[0]
                            b = nsubj_entry[1]
                            obj=self.Operations(name=index_dict[str(a)],source=index_dict[str(b)],dest=index_dict[str(b)],sentence=list(sentence.keys())[0])
                            self.op_list.append(obj)


            #function calls to inner functions
            tr11()
            tr12()
            tr13()
            tr14()
            tr15()
            tr16()
            tr17()
            tr18()
            tr19()
            tr20()
            tr21()
            tr22()
            tr23()
            tr24()
            tr25()
            tr26()
            tr27()
            tr28()
            tr29()
            tr30()
            tr31() 
            tr32()
            tr33()
            tr34()
            tr35()
            tr36()
            tr37()
            tr38()
            tr39()
            # tr40()
            # tr41()
            # tr42()
            # tr43()        

            #op_list containing all the operations                                       
            # for item in self.op_list:
            #     print(item)
            

    def tr44(self):
        """
        If op.SourceEntityTerm is not present in ClassDiagram Instance 
        then class = createClass(op.SourceEntityTerm,“<<entity class>>”);
        """      
        for op in self.op_list:
            find=False
            if op.SourceEntityTerm not in self.class_dict:
                for className in self.class_dict:
                    if op.SourceEntityTerm in self.class_dict[className]["Attribute"]:
                        find=True
                        break
                if find==False:
                    self.class_dict[op.SourceEntityTerm]={"Attribute":[],"Behavior":{}}
                
    
    def tr45(self):
        """
        For each class C in ClassDiagram Instance
            If (op.DestEntityTerm.name==C.name)AND(C does not contain operation op.name(op.Para)) 
                then C.addOperation(op.name(op.Para)); 
            EndIf
        EndFor
        If no such class is found then
            For each class C in ClassDiagram Instance
                If(op.DestEntityTerm.name==a.name for some attribute a of class C)AND (C does not contains operation op.name(op.Para)) 
                    then C.addOperation(op.name(op.Para)); 
                EndIf
            EndFor 
        EndIf
        If no such class is found 
            then C=createClass(op.DestEntityTerm.name,“<<entity class>>”); 
            C.addOperation(op.name(op.Para));
        EndIf
        """
        
        for op in self.op_list:
            findClass = False
            #print(op.name,"....",op.para)
            for className in self.class_dict:
                if op.DestEntityTerm == className:
                    if op.name not in self.class_dict[className]["Behavior"]:
                        self.addBehaviorToClass(className, op.name, op.para)
                        findClass=True
                        #print(1)
                    else:
                        if op.para not in self.class_dict[className]["Behavior"][op.name]:
                            self.addBehaviorToClass(className, op.name, op.para)
                            findClass=True
                            #print(2)
            if findClass == False:
                for className in self.class_dict:
                    for eachAttribute in self.class_dict[className]:
                        if op.DestEntityTerm == eachAttribute:
                            if op.name not in self.class_dict[className]["Behavior"]:
                                self.addBehaviorToClass(className, op.name, op.para)
                                findClass=True
                                #print(3)
                                break
                            else:
                                if op.para not in self.class_dict[className]["Behavior"][op.name]:
                                    self.addBehaviorToClass(className, op.name, op.para)
                                    findClass=True
                                    #print(4)
                                    break
            if findClass  == False:
                self.addBehaviorToClass(className, op.name, op.para)

                
                
    def tr46(self):
        """   
        For each relationship r in ClassDiagram Instance
            If(op.SourceEntityTerm==r.class1 and op.DestEntityTerm==r.class2)AND(r.name does not contains op.name)
                append op.name to r.name 
            EndIf
        EndFor
        If (no such relationship found) then
            For each class c in ClassDiagram Instance 
                If(op.DestEntityTerm==c.Name)
                    rName=op.name; 
                    createRelationship(op.SourceEntityTerm, c, rName, “association”); 
                EndIf
            EndFor
            If(no such class is found) then
                For each class c in ClassDiagram Instance 
                    If(op.DestEntityTerm==a.Name for some attribute a in class c)
                        rName=op.name; 
                        createRelationship(op.SourceEntityTerm, c, rName, “association”); 
                    EndIf
                EndFor 
            EndIf
        EndIf
        """
        print(self.relationship_dict)
        temp = self.relationship_dict
        print(len(self.op_list))


        for op in self.op_list:
            #print(op)
            findRelationship = False
            for rel_name in temp:
                for relationship in temp[rel_name]:
                    if op.SourceEntityTerm==relationship[0] and op.DestEntityTerm==relationship[1]:
                        #print(op)
                        #print(relationship)
                        if op.name not in relationship[2]:
                            relationship[2].append(op.name)
                            print(1)
                            findRelationship=True
            if findRelationship==False:
                for rel_name in temp:
                    for relationship in temp[rel_name]:
                        if relationship[1] in self.class_dict:
                            if op.SourceEntityTerm==relationship[0] and op.DestEntityTerm in self.class_dict[relationship[1]]["Attribute"]:
                                if op.name not in relationship[2]:
                                    relationship[2].append(op.name)
                                    findRelationship=True
                                    print(2)
                        
                        for className in self.class_dict:
                            for eachAttribute in self.class_dict[className]:
                                if op.SourceEntityTerm==relationship[0] and op.DestEntityTerm==eachAttribute and op.name not in relationship[2]:
                                    relationship[2].append(op.name)
                                    findRelationship=True
        
        
        
            if findRelationship==False:
                self.addToRelationshipDict(op.SourceEntityTerm, op.DestEntityTerm, [op.name], "association")
                #print(2)
        #print(temp)

    def tr51(self):
        """
        For each of the two classes c1 and c2 in ClassDiagram Instance
            If c2 is attribute of c1 then
                aggregateClass=c1;partClass=c2;
                createRelationship(aggregateClass,partClass,“aggregation”);
            EndIf
        EndFor
        """
        for class1 in self.class_dict:
            for class2 in self.class_dict:
                if class1 != class2:
                    if class2 in self.class_dict[class1]["Attribute"]:
                        aggregateClass = class1
                        partClass = class2
                        self.addToRelationshipDict(aggregateClass,partClass,[],"aggregation")
        
    def tr52(self,word_list,pos_tags):
        """
        For each sentence of type Part-AggSubString-Whole, the POS-tags of the sentence are scanned and
            wholeClass=createClass(noun nr on the right of AggSubString,“<<entity class>>”);
            For each noun nl on the left of AggSubString
                partClass=createClass(nl,“<<entity class>>”);
                createRelationship(wholeClass,partClass,“aggregation”);
            EndFor
        EndFor        
        """
        np_list = pos_tags["NP"]
        vp_list = pos_tags["VP"]
        
        noun_list = []
        if "NN" in pos_tags:
            noun_list += pos_tags["NN"]
        if "NNS" in pos_tags:
            noun_list += pos_tags["NNS"]
        if "NNP" in pos_tags:
            noun_list += pos_tags["NNP"]
        if "NNPS" in pos_tags:
            noun_list += pos_tags["NNPS"]
        noun_list = list(set(noun_list))    
        
        sentence_lemma = " ".join(word_list)
        
        for key in ["be part of", "be unit of", "be member of"]:
            part_list = []
            whole_list = []
            if key in sentence_lemma:
                key_word = key.split(" ")
                vp_start = word_list.index(key_word[0])+1
                np_start = vp_start + len(key_word)
                
                np_end = 10000
                for np in np_list:
                    if np[0] == np_start and np[1] < np_end:
                        np_end = np[1]
                    
                for word in range(np_start, np_end+1):
                    if (word,word) in noun_list:
                        whole_list.append(word_list[word-1])
                        self.class_dict[word_list[word-1]]={"Attribute":[],"Behavior":{}}
                                
                np_start = 0
                np_end = vp_start-1
                for np in np_list:
                    if np[1] <= np_end and np[0] > np_start and np[0] != np[1]:
                        np_start = np[0]
                        
                for word in range(np_start,np_end+1):
                    if (word,word) in noun_list:
                        self.class_dict[word_list[word-1]]={"Attribute":[],"Behavior":{}}
                        for whole in whole_list:
                            self.addToRelationshipDict(whole, word_list[word-1], "", "aggregation")
        
    
    def tr53(self,word_list,pos_tags):
        """
        For each sentence of type Whole-AggSubString-Part, the POS-tags of the sentence are scanned and
            wholeClass=createClass(noun nl on the right of AggSubString,“<<entity class>>”);
            For each noun nr on the left of AggSubString
                partClass=createClass(nr,“<<entity class>>”);
                createRelationship(wholeClass, partClass, “aggregation”);
            EndFor
        EndFor        
        """
        np_list = pos_tags["NP"]
        vp_list = pos_tags["VP"]
        
        noun_list = []
        if "NN" in pos_tags:
            noun_list += pos_tags["NN"]
        if "NNS" in pos_tags:
            noun_list += pos_tags["NNS"]
        if "NNP" in pos_tags:
            noun_list += pos_tags["NNP"]
        if "NNPS" in pos_tags:
            noun_list += pos_tags["NNPS"]
        noun_list = list(set(noun_list))    

        sentence_lemma = " ".join(word_list)
        
        for key in ["consist of", "be make of", "contain", "be compose of"]:
            part_list = []
            whole_list = []
            if key in sentence_lemma:
                key_word = key.split(" ")
                vp_start = word_list.index(key_word[0])+1
                
                np_end = 0
                for np in np_list:
                    if np[1] > np_end and np[1] < vp_start:
                        np_start = np[0]
                        np_end = np[1]
                
                for word in range(np_start, np_end+1):
                    if (word,word) in noun_list:    
                        self.class_dict[word_list[word-1]]={"Attribute":[],"Behavior":{}}
                        whole_list.append(word_list[word-1])
                
                np_start = 10000
                np_end = 100000
                for np in np_list:
                    if np[0] > vp_start and np[1] < np_end:
                        np_start = np[0]
                        np_end = np[1]

                for word in range(np_start, np_end+1):
                    if (word,word) in noun_list:
                        self.class_dict[word_list[word-1]]={"Attribute":[],"Behavior":{}}
                        for whole in whole_list:
                            self.addToRelationshipDict(whole, word_list[word-1], "", "aggregation")
                            
    
    
    def tr54(self):
        """
        For each class c in ClassDiagram Instance
            If c is not present as EndClass in any relationship then
                c is deleted from ClassDiagram Instance
            EndIf
        EndFor        
        """
        for eachClass in list(self.class_dict.keys()):
            findRela = False
            for eachRela in self.relationship_dict:
                for rela in self.relationship_dict[eachRela]:
                    if eachClass in rela:
                        findRela = True
                        break
            if findRela == False:
                #print(findRela)
                del self.class_dict[eachClass]
    
        
            
    def addAttributeToClass(self,className,attributeName):
        if className not in self.class_dict:
            self.class_dict[className]={"Attribute":[attributeName], "Behavior":{}}
        else:
            self.class_dict[className]["Attribute"].append(attributeName)
            
    
    def addBehaviorToClass(self,className,behaviorName,para):
        if className not in self.class_dict:
            self.class_dict[className]={"Attribute":[], "Behavior":{behaviorName:[para]}}
        else:
            if behaviorName in list(self.class_dict[className]["Behavior"].keys()):
                self.class_dict[className]["Behavior"][behaviorName].append(para)
            else:
                self.class_dict[className]["Behavior"][behaviorName]=[para]
        
            
    def addToRelationshipDict(self,parentClass,childClass,relationshipName, relationship):
        if relationship not in self.relationship_dict:
            self.relationship_dict[relationship]=[[parentClass,childClass, relationshipName]]
        else:
            self.relationship_dict[relationship].append([parentClass,childClass, relationshipName])
            


if __name__ == '__main__':
    print(os.getcwd() + "/Data/input_origin/" + "2014-USC-Project02.txt")
    p = TransformationRules(os.getcwd() + "/Data/input_origin/" + "2014-USC-Project02.txt")
    p.apply_rules()



