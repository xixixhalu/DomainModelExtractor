import re
import os
import numpy as np
from spellchecker import SpellChecker
import collections
import itertools
import spacy
import en_core_web_sm
global nlp
from util.logger import Logger
global logger
import string
import nltk
import argparse

CHECK_EDIT_DISTANCE = 1
CORRECT_WORD_FREQUENCY = 2

class Misspelling:
    def __init__(self, file_name="", output_path="", input_str_list=[], api_mode=False):
        # Received params
        self.api_mode = api_mode
        self.file_name = file_name
        self.output_path = output_path
        self.input_str_list = input_str_list
        
        # Build-in params
        self._glossary_file = "./Glossary/glossary.txt"
        self._word_freq_count = {}
        self._word_candidate = []
        self._line_indx_dict = {}
        
        self._check_format()
    
    # check_format() is used to check if params and corresponding mode are matched.
    def _check_format(self):
        if self.api_mode:
            if len(self.input_str_list) == 0:
                try:
                    raise Exception()
                except Exception:
                    print("Error: API mode expect a input_str_list.")
        else:
            if self.file_name == "":
                try:
                    raise Exception()
                except Exception:
                    print("Error: FILE mode expect a file_name.")
            if self.output_path == "":
                try:
                    raise Exception()
                except Exception:
                    print("Error: FILE mode expect a output_path.")


    def _word_freq(self):
        regex = "((?!-)[A-Za-z0-9-]" + "{1,63}(?<!-)\\.)" + "+[A-Za-z]{2,6}"
        # reference:“https://www.geeksforgeeks.org/how-to-validate-a-domain-name-using-regular-expression/”
        pattern = re.compile(regex)
        if self.api_mode:
            fixed_input_str = '\n'.join(input_str_list)
            s = fixed_input_str.replace('\n', ' ').lower()
            s = re.sub(pattern, '', s)  # filter out domain name and URL in sentences
        else:
            with open(self.file_name, "r") as myfile:
                # return the word frequency in the entire file
                s = myfile.read().replace('\n', ' ').lower()
                s = re.sub(pattern, '', s)  # filter out domain name and URL in sentences
        del_str = string.punctuation
        replace_punctuation = ' ' * len(del_str)
        data = s.translate(str.maketrans(del_str, replace_punctuation))
        data = data.split(' ')
        fdist1 = nltk.FreqDist(data)
        
        self._word_freq_count = fdist1.most_common()
    
    
    def _word_detect(self, n):
        # output words with frequency n
        ret = []
        for word, freq in self._word_freq_count:
            if freq == n:
                ret.append(word)
        
        self._word_candidate = ret
    
    
    def _word_line_index(self):
        del_str = string.punctuation
        replace_punctuation = ' ' * len(del_str)
        line_indx_dict = {}
        if self.api_mode:
            sentence_list = self.input_str_list
        else:
            with open(self.file_name, "r") as myfile:
                sentence_list = myfile.readlines()
        # store the line index
        for indx, line in enumerate(sentence_list):
            line = line.strip().lower()
            line = line.translate(str.maketrans(del_str, replace_punctuation))
            fdist1 = nltk.FreqDist(line.split())
            for word, freq in fdist1.most_common():
                if freq == 1:
                    line_indx_dict[word] = indx+1
        
        self._line_indx_dict = line_indx_dict
        
    
    def _read_glossary(self):
        # output a list of strings in glossary file
        try:
            with open(self._glossary_file, "r") as myfile:
                ret = myfile.read().lower().split('\n')
        except:
            print(f"Please check self._glossary_file is in correct directory, current file path is: {self.glossary_file}")
        return ret


    def _spell_check(self):
        spell = SpellChecker(language='en', case_sensitive=True, distance=CHECK_EDIT_DISTANCE)
        correct_dict = {}

        # load glossary
        glossary = self._read_glossary()
        spell.word_frequency.load_words(glossary)

        # Add frequent word into self dict
        for word, freq in self._word_freq_count:
            if freq >= CORRECT_WORD_FREQUENCY:
                spell.word_frequency.add(word)
                
        incorrect_candidate = spell.unknown([w for w in self._word_candidate if len(w)>1])
        incorrect_words = list(incorrect_candidate)
        report_list = []
        # if exist incorrect_words
        if incorrect_words:
            for word in incorrect_words:
                if word in self._line_indx_dict:
                    correction = spell.correction(word)
                    if word.lower() != correction.lower():
                        suggested_words = []
                        if self.api_mode:
                            suggested_words = correction
                            msg = (word, str(self._line_indx_dict[word]),suggested_words)
                            report_list.append(msg)
                        else:
                            correct_dict[word] = correction
                            msg = word + ", line " + str(self._line_indx_dict[word]) + '\n'
                            logger.info("Unknown words: \n" + msg)
        # if not exist incorrect word
        else:
            print("No Unknown words")
            logger.info("No Unknown words")
        
        if self.api_mode:
            return report_list, incorrect_words
        else:
            return correct_dict, incorrect_words
        
        
    def _correctFile(self, file_origin_lines, file_preprocess_lines, correct_dict):
        correct_lines = []
        for idx in file_preprocess_lines:
            for sentence in file_preprocess_lines[idx]:
                correct_line = sentence
                for word in correct_dict:
                    # Bo: temporary matching pattern, may not suit for all cases due to capital letters and stemming/original format.
                    pattern = '(\W|^)' + re.escape(word) + '\\({0,1}e{0,1}s{0,1}\\){0,1}(\W)' #pattern = '(\W|^)' + word + 's{0,1}(\W)'
                    if re.search(pattern, correct_line): # case sensitive to avoid change of Proper noun
                        correct_line = re.sub(pattern, rf'\1{correct_dict[word]}\2', correct_line)
                        logger.warning("Change Line " + str(idx + 1) + ": " + "\n" + file_origin_lines[idx] + "Word: " + word + "\nChange to: " + correct_dict[word])
                correct_lines.append(correct_line)

        return correct_lines
        
        
    def run(self):
        self._word_freq()
        self._word_detect(1)
        self._word_line_index()
        if self.api_mode:
            return self._spell_check()
        else:
            correct_dict, _ = self._spell_check()
            correct_lines = self._correctFile(file_origin_lines, file_preprocess_lines, correct_dict)
            with open(self.output_path + '.corrected.txt', 'w') as outfile:
                outfile.writelines(correct_lines)


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
                        help='input file. Example: python3 misspelling.py -f 2014-USC-Project02')
    parser.add_argument('-o', '--output', type=str, metavar='', default="./output/misspelling_detect_1/",
                        help='output path. Default: %(default)s')
    parser.add_argument('-l', '--list', action='store_true',
                        help='list all input files. Example: python3 misspelling.py -l')
    parser.add_argument('-a', '--api_mode', type=bool, default=False, help='api mode. Default: %(default)s')
    args = parser.parse_args()

    if args.file:
        api_mode = True
        filename = args.file
        input_path = args.input + filename
        output_path = args.output + filename
        api_mode = args.api_mode

        nlp = spacy.load('en_core_web_sm')
        logger = Logger(output_path + '_log.txt')
        check_file=input_path+'.txt'
        if api_mode:
            input_str_list = []
            with open(input_path + '.txt') as testFile :
                input_str_list = testFile.readlines()
            
            misspelling_api_mode = Misspelling(input_str_list=input_str_list, api_mode=True)
            report_list, _ = misspelling_api_mode.run()
            print(report_list)
        else:
            file_origin_lines = {}
            file_preprocess_lines = {}
            with open(input_path + '.txt') as testFile :
                lines = testFile.readlines()
                for idx, line in enumerate(lines):
                    file_origin_lines[idx] = line
                    file_preprocess_lines[idx] = [line]

            misspelling_file_mode = Misspelling(file_name=check_file, output_path=output_path)
            misspelling_file_mode.run()

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
