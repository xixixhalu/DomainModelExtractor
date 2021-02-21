import re
import os
import numpy as np
from spellchecker import SpellChecker
import collections
import itertools
#import stanza
import spacy
import en_core_web_sm
from spacy.matcher import Matcher

nlp = spacy.load('en_core_web_sm')

def removeSlash(line) :
    doc = nlp(line) 
    result_line = []
    break_point  = []
    break_point_dict = {}
    slash_pos = []
    j = 0
    index = 0
    for w in doc :     
        if w.text == '/' or w.text =='and/or' :
            slash_pos.append(w.i)
            for i in range(1, w.i) :
                if doc[w.i - i].pos_ == doc[w.i+1].pos_ :
                    if doc[w.i-i-1].tag_ == 'HYPH' :
                        break_point.append(w.i-i-2)
                        break_point_dict[j] = [w.i-i-2]
                        break
                    else :
                        break_point.append(w.i-i)
                        break_point_dict[j] = [w.i-i]
                        break
            break_point.append(w.i+1)
            break_point_dict[j].append(w.i+1)
            j +=1
    #print(break_point_dict)
    j = 0
    dict_j = {}
    dict_j[0] = break_point_dict[0]
    for key in break_point_dict :
        if key != 0 :

            if break_point_dict[key-1][-1] == break_point_dict[key][0] :
                dict_j[j].extend(break_point_dict[key])
                dict_j[j] = list(collections.OrderedDict.fromkeys(dict_j[j]))  

            else :
                j+= 1
                dict_j[j] = break_point_dict[key]
    #print(dict_j)
    all_break_point = list(dict_j.values())
    
    comb_break_point = list(itertools.product(*all_break_point))
    comb_break_point = [list(ele) for ele in comb_break_point]         
    sentence_part = [[0,all_break_point[0][0]-1]]
    
    for i in range(1,len(all_break_point)) :
        part = [all_break_point[i-1][-1]+1,all_break_point[i][0]-1]
        sentence_part.append(part)

    sentence_part.append([all_break_point[-1][-1]+1, len(doc)-1])
    #print('sentence_part: ', sentence_part)
    #print('slash_pos:' , slash_pos)
    #print('all_break_point: ' , all_break_point)
    #print('comb_break_point', comb_break_point)
    
    for i in range(0, len(comb_break_point )):
        sentence = doc[sentence_part[0][0]:sentence_part[0][1]+1].text
        for k in range(0,len(comb_break_point[i])) :
            index = all_break_point[k].index(comb_break_point[i][k])
            new_start = sentence_part[k+1][0]
            
            if index < len(all_break_point[k])-1 :
                sentence += ' '+doc[all_break_point[k][index]:all_break_point[k][index+1]-1].text
                if doc[all_break_point[k][index+1]].pos_ != 'VERB' and doc[all_break_point[k][index+1]].pos_ != 'NOUN' :
                    new_start =  sentence_part[k+1][0]+1
            else :
                sentence += ' '+doc[comb_break_point[i][k]].text
                #j = 0
                if doc[comb_break_point[i][k]].pos_ != 'VERB' and doc[comb_break_point[i][k]].pos_ != 'NOUN' :
                    #print(doc[comb_break_point[i][k]+j])
                    #j+=1
                    new_start = sentence_part[k+1][0]+1
                   
                    sentence += ' '+doc[comb_break_point[i][k]+1].text
            sentence += ' '+doc[new_start:sentence_part[k+1][1]+1].text
                    
        result_line.append(sentence)
    return result_line
          

if __name__ == '__main__' :
    line1= "With this condition in place, as a general manger, I can monitor real-time twitter/facebook/instagram feeds/reaction from key sources in a continuous manner and/or on demand."
    line2 = "The system shall notify users about special events/campaigns so that user participation will increase."
    line3 ="As an administrator I can verify and/or approve comments from all users  to increase accuracy of information."
    line4 = "As a driver, I can check into/select a location through my mobile phone so that the I can pay for my valet."
    line5 ="As an admin I can edit the name of gateway/switch/floor/room."

    for line in removeSlash(line1) :
        print(line)