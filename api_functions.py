import dme_ui_api.misspelling
import re
from spellchecker import SpellChecker
import spacy
import en_core_web_sm
global nlp
import string
import nltk

import preprocessing
import ssr_matching
import rule_transforming
import visualizing

##########################################################
###         Start of misspelling.py                     ##
##########################################################
CHECK_EDIT_DISTANCE = 1
CORRECT_WORD_FREQUENCY = 2

def word_freq(input_str_list):
    regex = "((?!-)[A-Za-z0-9-]" + "{1,63}(?<!-)\\.)" + "+[A-Za-z]{2,6}"
    # reference:“https://www.geeksforgeeks.org/how-to-validate-a-domain-name-using-regular-expression/”
    pattern = re.compile(regex)
    fixed_input_str = '\n'.join(input_str_list)
    s = fixed_input_str.replace('\n', ' ').lower()
    s = re.sub(pattern, '', s)  # filter out domain name and URL in sentences
    del_str = string.punctuation
    replace_punctuation = ' ' * len(del_str)
    data = s.translate(str.maketrans(del_str, replace_punctuation))
    data = data.split(' ')
    fdist1 = nltk.FreqDist(data)

    return fdist1.most_common()


def word_line_index(input_str_list):
    del_str = string.punctuation
    replace_punctuation = ' ' * len(del_str)
    line_indx_dict = {}
    for indx, line in enumerate(input_str_list):
        line = line.strip().lower()
        line = line.translate(str.maketrans(del_str, replace_punctuation))
        fdist1 = nltk.FreqDist(line.split())
        for word, freq in fdist1.most_common():
            if freq == 1:
                line_indx_dict[word] = indx+1
    return line_indx_dict
    
    
def spell_check(word_candidate, word_freq, glossary_file, line_indx_dict):
    spell = SpellChecker(language='en', case_sensitive=True, distance=CHECK_EDIT_DISTANCE)

    # load glossary
    glossary = misspelling.read_glossary(glossary_file)
    spell.word_frequency.load_words(glossary)

    # Add frequent word into self dict
    for word, freq in word_freq:
        if freq >= CORRECT_WORD_FREQUENCY:
            spell.word_frequency.add(word)

    incorrect_candidate = spell.unknown([w for w in word_candidate if len(w)>1])
    incorrect_words = list(incorrect_candidate)
    report_list = []
    if incorrect_words:
        for word in incorrect_words:
            if word in line_indx_dict:
                suggested_words = []
                correction = spell.correction(word)
                if word.lower() == correction.lower():
                    continue
                else:
                    suggested_words = correction

                msg = (word, str(line_indx_dict[word]),suggested_words)
                report_list.append(msg)
    
    return report_list

    
def api_misspelling(input_str_list):
    nlp = spacy.load('en_core_web_sm')
    glossary_file="./Glossary/glossary.txt"
    
    file_origin_lines = {}
    file_preprocess_lines = {}
    report_list = []
    if len(input_str_list) > 0:
        for idx, line in enumerate(input_str_list):
            file_origin_lines[idx] = line
            file_preprocess_lines[idx] = [line]
    
        word_freq_count=word_freq(input_str_list)
        word_candidate=misspelling.word_detect(word_freq_count,1)
        line_indx_dict=word_line_index(input_str_list)
        # Passed logger as a new params.
        report_list = spell_check(word_candidate, word_freq_count, glossary_file, line_indx_dict)
    #    correct_lines = correctFile(file_origin_lines, file_preprocess_lines, correct_dict, logger)

    #    with open(output_path + '.corrected.txt', 'w') as outfile:
    #        outfile.writelines(correct_lines)
    return report_list

##########################################################
###         End of misspelling.py                       ##
##########################################################


##########################################################
###         Start of preprocessing.py                   ##
##########################################################

# preprocessing.py:
    # pre_process(): line 124, lines_no_slash no default type before for loop
def api_preprocessing(input_str_list):
    func_output, nonfunc_output, metadata, actors = [], [], [], []
    if len(input_str_list) > 0:
        p = preprocessing.PreProcessor()
        func_output, nonfunc_output, metadata, actors = p.api_pre_process(input_str_list)
    return func_output, nonfunc_output, metadata, actors

##########################################################
###         End of preprocessing.py                     ##
##########################################################
  
def api_diagram_generator(input_str_list):
    ## Preprocessing.py
    func_output, nonfunc_output, metadata, actors = api_preprocessing(input_str_list)
    
    ## ssr_matching.py
    ssr_output_result = ssr_matching.api_ssr_matching(func_output)
    
    ## rule_transforming.py
    transformed_output_result = rule_transforming.api_rule_transforming(ssr_output_result, actors, metadata)
    
    ## visualizing.py
    output_path = "./output/diagram_5/test_diagram_api"
    visualizing.UML_graphic(transformed_input, output_path)
    
#    return transformed_output_result


if __name__ == '__main__' :
    print("="*20)
    print("API for Domain Model Extractor")
    print("-"*20)
    
    print("Misspelling Test:")
    input_str_list = []
    with open('./Data/input_origin/2014-USC-Project08.txt') as testFile :
        input_str_list = testFile.readlines()

    report_list = api_misspelling(input_str_list)
    print(report_list)
    print("-"*20)
    print("Misspelling Correction Completed.")
    print("="*20)

#    print("Preprocessing Test:")
#    input_str_list = []
#    with open('./Data/input_origin/2014-USC-Project08.txt') as testFile :
#        input_str_list = testFile.readlines()
#
#    func_output, nonfunc_output, metadata, actors = api_diagram_generator(input_str_list)
#    print(metadata)
#    print("-"*20)
#    print("Preprocessing Completed.")
#    print("="*20)
    
#    print("Ssr_matching Test:")
#    with open('./Data/input_origin/2014-USC-Project08.txt') as testFile :
#        input_str_list = testFile.readlines()
#
#    ssr_output_result = api_diagram_generator(input_str_list)
#    print(ssr_output_result)
#    print("-"*20)
#    print("Ssr_matching Completed.")
#    print("="*20)
    
#    print("Rule_transforming Test:")
#    with open('./Data/input_origin/2014-USC-Project08.txt') as testFile :
#        input_str_list = testFile.readlines()
#
#    transformed_output_result = api_diagram_generator(input_str_list)
#    print(transformed_output_result)
#    print("-"*20)
#    print("Rule_transforming Completed.")
#    print("="*20)
    
    print("Visualizing Test:")
    with open('./Data/input_origin/2014-USC-Project08.txt') as testFile :
        input_str_list = testFile.readlines()

#    transformed_output_result = api_diagram_generator(input_str_list)
    api_diagram_generator(input_str_list)
    print("-"*20)
    print("Visualizing Completed.")
    print("="*20)
    
