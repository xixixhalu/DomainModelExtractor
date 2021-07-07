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
    incorrect_dict = {}
    incorrect_candidate_mapper = {}
    # print(file_freq_word_dict)
    # print(noun_word_list)
    for w in noun_word_list:
        incorrect_candidate_mapper[w["lemma"].lower()] = w["lemma"]

    spell_checker = SpellChecker(language='en', case_sensitive=True, distance=CHECK_EDIT_DISTANCE)

    for word in file_freq_word_dict:
        # print(word + " : " + str(len(file_freq_word_dict[word])))
        if len(file_freq_word_dict[word]) >= CORRECT_WORD_FREQUENCY:
            spell_checker.word_frequency.add(word)
    incorrect_candidate = spell_checker.unknown([w["lemma"] for w in noun_word_list])
    for w in incorrect_candidate:
        incorrect_dict[w] = file_freq_word_dict[incorrect_candidate_mapper[w]]

    # Prepare logger message
    msg = ""
    for w in incorrect_dict:
        lines = [str(idx+1) for idx in incorrect_dict[w]]
        msg += w + ", line " + ','.join(lines) + '\n'
    logger.info("Unknown words: " + msg)

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
                # Bo: temporary matching pattern, may not suit for all cases due to capital letters and stemming/original format.
                pattern = '(\W|^)' + word + 's{0,1}(\W)'
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
                file_preprocess_lines[idx] = [line]

        # with open(input_path + '.txt') as testFile :
        #     lines = testFile.readlines()
        #     for idx, line in enumerate(lines):
        #         file_origin_lines[idx] = line
        #         try:
        #             line_no_bracket = removeBracket(line)
        #         except:
        #             logger.error("removeBracket: Cannot process Line " + str(idx) + "\n" + line)
        #             # line_no_bracket = line
        #             continue
        #         # print(line_no_bracket)
        #         try:
        #             line_no_slash_list = removeSlash(line_no_bracket)
        #         except:
        #             logger.error("removeSlash: Cannot process Line " + str(idx) + "\n" + line)
        #             # line_no_slash_list = line_no_bracket
        #             continue
        #         # print(line_no_slash_list)
        #         file_preprocess_lines[idx] = line_no_slash_list

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
        f_list = set()
        for f in files:
            f_list.add(f.split(".")[0])
        for f in sorted(f_list):
            print(f) 
    else:
        parser.print_help()


    