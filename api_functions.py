import misspelling
import preprocessing
import ssr_matching
import rule_transforming
import visualizing
from util.file_writer import FakeWriter
import base64
import re


def api_functional_check(input_str_list):
    FUNC_RE = '(A|a)s (the|a|an) .+(I|i|My|my) '
    count_func = 0
    count_nonfunc = 0
    for line in input_str_list:
        if re.search(FUNC_RE, line):
            count_func += 1
        else:
            count_nonfunc += 1
    return count_func


def check_misspelling(input_str_list):
    count_func = api_functional_check(input_str_list)
    misspelling_writer = FakeWriter()
    misspelling_logger = FakeWriter()
    spell_checker = misspelling.Misspelling(input_str_list=input_str_list, writer=misspelling_writer, logger=misspelling_logger)
    report_list, incorrect_words = spell_checker.run()
    count_msg = f"{count_func} functional requirement(s) found. \n\n"
    misspelling_msg = ""
    for item in report_list:
        misspelling_msg += f"Unknown word at Line {item[1]}\nSuggestion: {item[0]} -> {item[2]}\n\n"
    if incorrect_words:
        misspelling_msg += f'Some words which might be unknown: {incorrect_words}'
    if misspelling_msg == "":
        misspelling_msg = "No concerns found.\n"
        
    return count_msg + misspelling_msg


def _api_preprocessing(input_str_list):
    func_writer = nonfunc_writer = meta_writer = actor_writer = logger = FakeWriter()
    p = preprocessing.PreProcessor(input_str_list=input_str_list, func_writer=func_writer, nonfunc_writer=nonfunc_writer, meta_writer=meta_writer, actor_writer=actor_writer,logger=logger)
    func_output, nonfunc_output, metadata, actors = p.pre_process()
    return func_output, nonfunc_output, metadata, actors
    

def _api_ssr_matching(func_output, rule_path="./SSR/SSR.xlsx"):
    ssr_writer = logger = FakeWriter()
    ssr_result = ssr_matching.ssr_matching_run(input_str_list=func_output, writer=ssr_writer, logger=logger,rule_path=rule_path)
    return ssr_result
                

def _api_rule_transforming(ssr_output_result, actors, metadata, transforming_rule="./TR/TR.xlsx"):
    transform_writer = FakeWriter()
    logger = FakeWriter()
    transformer = rule_transforming.Transformation(actors=actors, meta=metadata, ssr=ssr_output_result, writer=transform_writer, logger=logger)
    transformed_obj = transformer.run(transforming_rule=transforming_rule)
    return transformed_obj
                
              
def diagram_generator(input_str_list):
    error_output = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII='
    func_count = api_functional_check(input_str_list)
    if func_count == 0:
        return (error_output, 'png', "\nNo functional requirements for model generation.\n")
    try:
        ## Preprocessing
        func_output, nonfunc_output, metadata, actors = _api_preprocessing(input_str_list)
        ## ssr_matching
        ## Default param: rule_path="./SSR/SSR.xlsx"
        ssr_output_result = _api_ssr_matching(func_output)
        ## rule_transforming
        ## Default param: transforming_rule="./TR/TR.xlsx"
        transformed_output_result = _api_rule_transforming(ssr_output_result, actors, metadata)
        ## visualizing.py
        output_img, output = visualizing.UML_graphic(transformed_output_result)
        img_base64 = base64.b64encode(output_img[0]).decode('utf-8')
    except:
        return (error_output, 'png', "\nSome lines cannot be successfully processed.\nPossbile reasons: incomplete sentences, special characters, etc.\nPlease try to generate partial model with one or more win condition(s).\n")
    
    return (img_base64, output_img[1], "\nModel generated!\n")


if __name__ == '__main__' :
#    print("Misspelling Test:")
#    misspelling_input_str_list = []
#    with open('./Data/input_origin/2014-USC-Project08.txt') as testFile :
#        misspelling_input_str_list = testFile.readlines()
#
#    report_msg = check_misspelling(misspelling_input_str_list)
#    print(report_msg)
#    print("-"*20)
#    print("Misspelling Correction Completed.")
    
    print("Diagram Generator Test:")
    diagram_input_str_list = []
    with open('./output/misspelling_detect_1/2014-USC-Project02.corrected.txt') as testFile :
        diagram_input_str_list = testFile.readlines()

    #msg => (img_base64, output[1], "\nModel generated!\n")
    msg = diagram_generator(diagram_input_str_list)
    imgdata = base64.b64decode(msg[0])
    with open('2014-USC-Project02'+'.png', 'wb') as f:
        f.write(imgdata)
    print("Diagram Generation Completed.")
