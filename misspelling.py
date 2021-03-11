import re
import os
import numpy as np
from spellchecker import SpellChecker
import collections
import itertools
#import stanza
import spacy
import en_core_web_sm
global nlp

from util.logger import Logger
global logger

import argparse

CHECK_EDIT_DISTANCE = 1
CORRECT_WORD_FREQUENCY = 2

def removeSlash(line) :
    if '/' not in line :
        return [line]

    doc = nlp(line) 
    result_line = []
    break_point  = []
    break_point_dict = {}
    slash_pos = []
    j = 0
    index = 0
    # for w in doc:
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
        if w.text.startswith('('):
            remove_index.append(w.i)
        elif w.text.startswith(')'):
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
            
def frequentWordGen (lines) :
    file_freq_word_dict = {}
    noun_word_list = []
    for idx in lines:
        for sentence in lines[idx]:
            doc = nlp(sentence)
            for word in doc :
                if word.tag_ == 'NN' or word.tag_ == 'NNP' or word.tag_ == 'NNPS' or word.tag_ == 'NNS' :
                    noun_word_list.append({"text" : word.text,
                                          "lemma" : word.lemma_,
                                          "tag" : word.tag_,
                                          "line" : idx})
                    # print(noun_word_list)
                    if word.lemma_ in file_freq_word_dict:
                        file_freq_word_dict[word.lemma_].add(idx)
                    else:
                        file_freq_word_dict[word.lemma_] = {idx}
    # print(file_freq_word_dict)
    # print(noun_word_list)
    return file_freq_word_dict, noun_word_list

def spellcheck (file_freq_word_dict, noun_word_list) :
    '''
    Bo: 
    Add those words which appear more than CORRECT_WORD_FREQUENCY times to the dictionary.
    Check those words which appear only once.
    '''
    correct_dict = {}
    noun_list = []
    word_line = {}
    # print(file_freq_word_dict)
    # print(noun_word_list)

    spell_checker = SpellChecker(language='en', case_sensitive=True, distance=CHECK_EDIT_DISTANCE)

    for word in file_freq_word_dict:
        # print(word + " : " + str(len(file_freq_word_dict[word])))
        if len(file_freq_word_dict[word]) >= CORRECT_WORD_FREQUENCY:
            spell_checker.word_frequency.add(word)
    incorrect_candidate = spell_checker.unknown([w["lemma"] for w in noun_word_list])
    logger.info("Unknown words: " + str(incorrect_candidate))

    for candidate in incorrect_candidate :
        correction = spell_checker.correction(candidate)
        if (candidate.lower() == correction.lower()):
            continue
        else:
            correct_dict[candidate] = correction

    return correct_dict
    # reduced_incorrect_candidate = []
    # for candidate in incorrect_candidate :
    #     for word in file_freq_word_dict :
    #         if candidate == word.lower() :
    #             if file_freq_word_dict[word] >=2 or word.isupper() or (not word.isupper() and not word.islower()):
    #                 spell.word_frequency.add(candidate)
    #             else :
    #                 reduced_incorrect_candidate.append(candidate)
    # #print('reduced: ',reduced_incorrect_candidate)
    # for word in reduced_incorrect_candidate :
    #     correct_dict[word] = spell.correction(word)
    #     correct_candidate_dict[word] = spell.candidates(word)
    # return correct_dict, correct_candidate_dict

def correctFile(file_origin_lines, file_preprocess_lines, correct_dict, file_freq_word_dict):
    correct_lines = []
    for idx in file_preprocess_lines:
        for sentence in file_preprocess_lines[idx]:
            correct_line = sentence
            for word in correct_dict:
                pattern = '(\W|^)' + word + '.{0,1}(\W|$)'
                if re.search(pattern, correct_line): # case sensitive to avoid change of Proper noun
                    correct_line = re.sub(pattern, rf'\1{correct_dict[word]}\2', correct_line)
                    logger.warning("Change Line " + str(idx + 1) + ": " + "\n" + file_origin_lines[idx] + "Word: " + word + "\nChange to: " + correct_dict[word])
            correct_lines.append(correct_line)

    return correct_lines

if __name__ == '__main__' :
    
    #line1= "With this condition in place, as a general manger, I can monitor real-time twitter/facebook/instagram feeds/reaction from key sources in a continuous manner and/or on demand."
    #line2 = "The system shall notify users about special events/campaigns so that user participation will increase."
    #line3 ="As an administrator I can verify and/or approve comments from all users  to increase accuracy of information."
    #line4 = "As a driver, I can check into/select a location through my mobile phone so that the I can pay for my valet."
    #line5 ="As an admin I can edit the name of gateway/switch/floor/room."
    #line6 = 'If there is a conflict (there is already information in the row for the designated table) the application must be able to generate and execute  a PostgreSQL UPDATE statement for the "crawled" dataset.'
    #line7 = 'As a GM, my data can seamlessly integrate with the SporTech B.I. system in a standard compliant manner. (READ: The system shall communicate in PostgreSQL.).'
    
    parser = argparse.ArgumentParser(description='Misspelling Detection')
    parser.add_argument('-i', '--input', type=str, metavar='', default="./Data/input_origin/",
                        help='input path. Default: %(default)s')
    parser.add_argument('-f', '--file', type=str, metavar='',
                        help='input file. Example: python3 misspelling.py -f 2014-USC-Projecct02')
    parser.add_argument('-o', '--output', type=str, metavar='', default="./output/misspelling_detect_1/",
                        help='output path. Default: %(default)s')
    parser.add_argument('-l', '--list', action='store_true',
                        help='list all input files. Example: python3 misspelling.py -l')
    args = parser.parse_args()

    if args.file:
        filename = args.file
        input_path = args.input + filename
        output_path = args.output + filename
        # filename = '2014-USC-Project02'
        # input_path = './Data/input_origin/' + filename
        # output_path = './output/misspelling_detect_1/' + filename 
        nlp = spacy.load('en_core_web_sm')
        logger = Logger(output_path + '_log.txt')

        file_origin_lines = {}
        file_preprocess_lines = {}
        with open(input_path + '.txt') as testFile :
            lines = testFile.readlines()
            for idx, line in enumerate(lines):
                file_origin_lines[idx] = line
                try:
                    line_no_bracket = removeBracket(line)
                except:
                    logger.error("removeBracket: Cannot process Line " + str(idx) + "\n" + line)
                    # line_no_bracket = line
                    continue
                # print(line_no_bracket)
                try:
                    line_no_slash_list = removeSlash(line_no_bracket)
                except:
                    logger.error("removeSlash: Cannot process Line " + str(idx) + "\n" + line)
                    # line_no_slash_list = line_no_bracket
                    continue
                # print(line_no_slash_list)
                file_preprocess_lines[idx] = line_no_slash_list

        file_freq_word_dict, noun_word_list = frequentWordGen(file_preprocess_lines)
        correct_dict = spellcheck(file_freq_word_dict, noun_word_list)

        correct_lines = correctFile(file_origin_lines, file_preprocess_lines, correct_dict, file_freq_word_dict)
        with open(output_path + '.corrected.txt', 'w') as outfile:
            outfile.writelines(correct_lines)
      
        #for word in nlp('As a SporTech B.I. contractor, I can  add,delete,update the specific websites visited,  fields to capture from the website and frequency of crawler refreshes for each specified website.') :
        #    print(word,word.pos_)
    elif args.list:
        input_path = args.input
        files = os.listdir(input_path)
        for f in files:
            print(f.split(".")[0])
    else:
        parser.print_help()


    