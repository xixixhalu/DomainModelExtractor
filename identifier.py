import json
import pprint
import re
import os
import glob

from sys import exc_info


from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *

from util.file_op import fileOps

filter_type = set(["[u'compound-1']", \
                    "[u'compound-1', u'compound']"
                ])

class Identifier:
    def __init__(self):
        self.__printer = pprint.PrettyPrinter(indent=2)
        self.__final_result = {}
        self.__final_set = set()

    def __preprocess(self, sentence):
        #TODO:Remove "As a $role" and replace the "I/my" with "$role/$role's"
        return
        
    def clear(self):
        self.__final_result.clear()
        self.__final_result = {}
        self.__final_set.clear()

    def display(self, title, content):
        print '[' + title + ']'
        if title == 'Sentence':
            print content
            index = ''
            begin, end = 0, 0
            for elem in self.__output['sentences'][0]['tokens']:
                end = elem['characterOffsetEnd']
                for i in range(begin, end - len(str(elem['index']))):
                    index += ' '
                if re.match("^[,.]*$", elem['word']):
                    continue;
                index += str(elem['index'])
                begin = end
            print index
        elif type(content) is dict:
            print self.__printer.pprint(content)
        else:
	        print content

    def __traceBack(self, entity1, entity2):
        #TODO: Figure out the relationship between entity1 and entity2 in terms of TDs
        '''
        Example1:
        Step1: NN + NNP + NNS : 3, 9, 10, 17, 18
        Step2: 3, compond(9, 10), compound(17, 18)
        Step3: nsubj(5,7), nsubj(13, 15), dobj(7, 10), dobj(15, 18)
        Step4: ?(3,5), ?(3, 13)

        Example2:
        Like OpenIE
        '''

        # reutrn ()
        return

    def buildTDAdjacencyList(self, td_result):
        result = [[] for i in range(self.__tokenNum + 1)]
        for key, value in td_result.items():
            result[key[0]].append((key[1], value))
        return result

    def testTDNoCycle(self, td_adjacency_list):
        in_degree = [0 for i in range(self.__tokenNum + 1)]
        for i in range(self.__tokenNum):
            for e in td_adjacency_list[i]:
                in_degree[e[0]] += 1

        stack = []
        pop_count = 0
        for i in range(self.__tokenNum):
            if in_degree[i] == 0:
                stack.append(i)
        while(stack):
            node_id = stack[-1]
            stack.pop()
            pop_count += 1
            for e in td_adjacency_list[node_id]:
                in_degree[e[0]] -= 1
                if in_degree[e[0]] == 0:
                    stack.append(e[0])

        if pop_count == self.__tokenNum + 1:
            return True
        return False


    def getNounRelations(self, pt_result, td_adjacency_list):
        def DFS(id, result):
            noun_path_lists = []
            for e in td_adjacency_list[id]:
                path_list = DFS(e[0], result)
                for item in path_list:
                    item[1].append(e[1])
                noun_path_lists.append(path_list)
            l = len(noun_path_lists)
            for i in range(l):
                for j in range(i + 1, l):
                    list_i = noun_path_lists[i]
                    list_j = noun_path_lists[j]
                    for item_i in list_i:
                        for item_j in list_j:
                            id_1, path_1 = item_i[0], item_i[1]
                            id_2, path_2 = item_j[0], item_j[1]
                            if id_1 > id_2:
                                id_1, id_2 = id_2, id_1
                                path_1, path_2 = path_2, path_1

                            path = []
                            for dep in path_1:
                                path.append(dep + '-1')
                            path.extend(path_2[::-1])
                            result[(id_1, id_2)] = path

            new_noun_path_list = []
            for path_list in noun_path_lists:
                new_noun_path_list.extend(path_list)

            if id in noun_idx:
                for item in new_noun_path_list:
                    id_child = item[0]
                    path_child = item[1]
                    if id < id_child:
                        result[(id, id_child)] = path_child[::-1]
                    else:
                        path = []
                        for dep in path_child:
                            path.append(dep + '-1')
                        result[(id_child, id)] = path
                new_noun_path_list.append((id, []))
            return new_noun_path_list


        result = {}
        noun_idx = set()


        if 'NN' in pt_result:
            for item in pt_result['NN']:
                noun_idx.add(item[0])
                
                noun = self.__output['sentences'][0]['tokens'][item[0]-1 : item[1]]
                target_word = ' '.join([d["word"] for d in noun])
                if not target_word in self.__final_set:
                    self.append("NN", target_word)
                    self.__final_set.add(target_word)
        '''         
        if 'NNS' in pt_result:
            for item in pt_result['NNS']:
                noun_idx.add(item[0])

                noun = self.__output['sentences'][0]['tokens'][item[0]-1 : item[1]]
                target_word = ' '.join([d["word"] for d in noun])
                if not target_word in self.__final_set:
                    self.append("NNS", target_word)
                    self.__final_set.add(target_word)
        '''
        if 'NNP' in pt_result:
            for item in pt_result['NNP']:
                noun_idx.add(item[0])
                
                noun = self.__output['sentences'][0]['tokens'][item[0]-1 : item[1]]
                target_word = ' '.join([d["word"] for d in noun])
                if not target_word in self.__final_set:
                    self.append("NNP", target_word)
                    self.__final_set.add(target_word)

        '''
        if 'NNPS' in pt_result:
            for item in pt_result['NNPS']:
                noun_idx.add(item[0])
                
                noun = self.__output['sentences'][0]['tokens'][item[0]-1 : item[1]]
                target_word = ' '.join([d["word"] for d in noun])
                if not target_word in self.__final_set:
                    self.append("NNPS", target_word)
                    self.__final_set.add(target_word)
        '''

        DFS(0, result)
        return result


    def identify(self, sentence):
        self.__output = analyze(sentence)
        if self.__output is None:
            return None

        td_result = TypeDep(self.__output)
        pt_result = parsePosTag(self.__output)

        self.display('Sentence', sentence)
        self.display('Type Dependency', td_result)
        self.display('Pos-Tag', pt_result)
        
        self.__tokenNum = len(self.__output['sentences'][0]['tokens'])

        td_adjacency_list = self.buildTDAdjacencyList(td_result)

        td_no_cycle = self.testTDNoCycle(td_adjacency_list)

        
        #self.display("Type Dependency - No Cycle Test", td_no_cycle)


        noun_relations = self.getNounRelations(pt_result, td_adjacency_list)

        self.display('Noun Relations', noun_relations)
        #return noun_relations

        for key, value in noun_relations.items():

            if not str(value) in filter_type:
                continue
          
            noun = self.__output['sentences'][0]['tokens'][key[0]-1 : key[1]]
            target_word = ' '.join([d["word"] for d in noun])
            if not target_word in self.__final_set:
                self.append(value, target_word)
                self.__final_set.add(target_word)
            
        return self.__final_result
        
    def append(self, key, value):
        if not str(key) in self.__final_result:
            self.__final_result[str(key)] = []
        self.__final_result[str(key)].append(value)
    
	
if __name__ == '__main__':

    sentence = 'As a user, I can use my WAT_points to redeem items from a virtual store.'
    identifier = Identifier()
    identifier.identify(sentence)