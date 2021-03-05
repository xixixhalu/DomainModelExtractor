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
    if '/' not in line :
        #print('not found')
        return [line]
    #for w in doc:
    #    print(w,w.pos_)
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
            if j not in break_point_dict :
                break_point_dict[j] = [w.i-1]    
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
                    for n in range(1, len(doc)-1-comb_break_point[i][k]) :

                        sentence += ' '+doc[comb_break_point[i][k]+n].text
                        if doc[comb_break_point[i][k]+n].pos_ == 'VERB' or doc[comb_break_point[i][k]+n].pos_ ==' NOUN' :
                            new_start = comb_break_point[i][k]+n
                            break
            
            sentence += ' '+doc[new_start:sentence_part[k+1][1]+1].text
            
        result_line.append(sentence)
    return result_line

def removeBracket(line) :
    doc = nlp(line) 
    result_line = []
    remove_index = []
    for w in doc :
        if w.text == '(' :
            remove_index.append(w.i)
        elif w.text == ')' :
            remove_index.append(w.i)
        else :
            continue
    if remove_index == [] :
        return line
    sentence = ''

    if remove_index[0] == 0 :
        sentence_start = remove_index[1] +1
        index_start = 2
    else :
        sentence_start = 0
        index_start = 0

    for i in range(index_start,len(remove_index)) :
        if i % 2 != 0 :
            sentence_start = remove_index[i]+1
        else :
            sentence += doc[sentence_start:remove_index[i]].text + ' '
    sentence += doc[remove_index[-1]+1:len(doc)].text
    return sentence
            
def frequentWordGen (file) :
    file_freq_word_dict = {}
    noun_word_list = [] 
    for line in file:
            doc = nlp(line)
            for word in doc :
                if word.pos_ == 'NOUN' or word.pos_ == 'PRON' or word.pos_ == 'PROPN' or word.pos_ == 'NN' or word.pos_ == 'NNP' or word.pos_ == 'NNPS' or word.pos_ == 'NNS' :
                    noun_word_list.append(word.lemma_)
                    if word.lemma_ in file_freq_word_dict :
                        file_freq_word_dict[word.lemma_] += 1
                    else :
                        file_freq_word_dict[word.lemma_] = 1
    print(file_freq_word_dict)
    return file_freq_word_dict, noun_word_list

def spellcheck (file_freq_word_dict, noun_word_list,spell) :
    correct_dict = {}
    correct_candidate_dict = {}
    #print(file_freq_word_dict)
    incorrect_candidate = spell.unknown(noun_word_list)
    #print('incorrect: ', incorrect_candidate)
    reduced_incorrect_candidate = []
    for candidate in incorrect_candidate :
        for word in file_freq_word_dict :
            if candidate == word.lower() :
                if file_freq_word_dict[word] >=2 or word.isupper() or (not word.isupper() and not word.islower()):
                    spell.word_frequency.add(candidate)
                else :
                    reduced_incorrect_candidate.append(candidate)
    #print('reduced: ',reduced_incorrect_candidate)
    for word in reduced_incorrect_candidate :
        correct_dict[word] = spell.correction(word)
        correct_candidate_dict[word] = spell.candidates(word)
    return correct_dict, correct_candidate_dict

def correctFile(file_preprocess_lines, correct_dict) :
    correct_lines = []
    for line in file_preprocess_lines :
        correct_line = line
        for word in correct_dict :
            insensitive = re.compile(re.escape(word), re.IGNORECASE)
            correct_line = insensitive.sub(correct_dict[word],line)
        correct_lines.append(correct_line)
    return correct_lines



if __name__ == '__main__' :
    spell = SpellChecker(language='en',case_sensitive=False,distance=1)
    #line1= "With this condition in place, as a general manger, I can monitor real-time twitter/facebook/instagram feeds/reaction from key sources in a continuous manner and/or on demand."
    #line2 = "The system shall notify users about special events/campaigns so that user participation will increase."
    #line3 ="As an administrator I can verify and/or approve comments from all users  to increase accuracy of information."
    #line4 = "As a driver, I can check into/select a location through my mobile phone so that the I can pay for my valet."
    #line5 ="As an admin I can edit the name of gateway/switch/floor/room."
    #line6 = 'If there is a conflict (there is already information in the row for the designated table) the application must be able to generate and execute  a PostgreSQL UPDATE statement for the "crawled" dataset.'
    #line7 = 'As a GM, my data can seamlessly integrate with the SporTech B.I. system in a standard compliant manner. (READ: The system shall communicate in PostgreSQL.).'
    
    file_preprocess_lines = []
    with open('./Data/input_origin/2014-USC-Project01.txt') as testFile :
        lines = testFile.readlines()
        file_freq_word_dict, noun_word_list = frequentWordGen(lines)
        for line in lines:
            line_no_bracket =  removeBracket(line)
            #print(line_no_bracket)
            line_no_slash_list = removeSlash(line_no_bracket)
            #print(line_no_slash_list)
            file_preprocess_lines.extend(line_no_slash_list)
    correct_dict, correct_candidate_dict = spellcheck(file_freq_word_dict, noun_word_list,spell)
    correct_lines = correctFile(file_preprocess_lines, correct_dict)
    with open('./output/corrected_2014-USC-Project01.text', 'w') as outfile:
        outfile.writelines(correct_lines)

    with open('./output/mispellDetection01.text','w') as outfile1 :
        for word in correct_dict :
            outfile1.write(word+','+correct_dict[word]+','+str(correct_candidate_dict[word])+'\n')    
    #for word in nlp('As a SporTech B.I. contractor, I can  add,delete,update the specific websites visited,  fields to capture from the website and frequency of crawler refreshes for each specified website.') :
    #    print(word,word.pos_)