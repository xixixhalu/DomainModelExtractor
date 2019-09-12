import sys
sys.path.append('./')
sys.path.append('../')

import json
import pprint
import re

from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *

class Identifier:
    def __init__(self):
        self.__printer = pprint.PrettyPrinter(indent=2)

    def __preprocess(self, sentence):
        #TODO:Remove "As a $role" and replace the "I/my" with "$role/$role's"
        return
        

    def __display(self, title, content):
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

    def identify(self, sentence):
        self.__output = analyze(sentence)
        td_result = TypeDep(self.__output)
        pt_result = parsePosTag(self.__output)

        self.__display('Sentence', sentence)
        self.__display('Type Dependency', td_result)
        self.__display('Pos-Tag', pt_result)

	
if __name__ == '__main__':
    #sentence = 'As a user, I can redeem usable WAT points so that I can receive a gift card.'
    #sentence = 'As a user, I can like/dislike an answer so that other users can gauge the credibility of the answer.'
    #sentence = 'As a user, I can view other users\' profiles so that I can see their information and points.'
    #sentence = 'As a user, I can view the leaderboard by sorting it either based on Schools or graduation date.'
    sentence = 'As a user, I can use my points of WAT to redeem items from a virtual store.'
    identifier = Identifier()
    identifier.identify(sentence)
