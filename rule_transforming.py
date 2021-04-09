import os
import sys
import traceback
import pygtrie as trie
import json
from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *

# from UMLViewer import *
import re

from util.logger import Logger
global logger

from util.IS import *

import argparse


class Transformation:
    def __init__(self, filename, ssr_input_path, pre_input_path):
        self.ssr_file_path = ssr_input_path + filename + "ssr.txt"
        self.actor_file_path = pre_input_path + filename + ".actor.txt"
        self.meta_file_path = pre_input_path + filename + ".meta.txt"
        self.domain = ISDomain(filename)

    def identify_actor(self):
        return 0

    def apply_rules(self):
        return 0

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Rule Transformation')
    parser.add_argument('-s', '--inputssr', type=str, metavar='', default="./output/ssr_match_3/",
                        help='SSR result path. Default: %(default)s')
    parser.add_argument('-p', '--inputpre', type=str, metavar='', default="./output/preprocessing_2/",
                        help='Preprocessing result path. Default: %(default)s')
    parser.add_argument('-f', '--file', type=str, metavar='',
                        help='input file. Example: python3 rule_transforming.py -f 2014-USC-Projecct02')
    parser.add_argument('-o', '--output', type=str, metavar='', default="./output/tr_process_4/",
                        help='output path. Default: %(default)s')
    parser.add_argument('-l', '--list', action='store_true',
                        help='list all input files. Example: python3 rule_transforming.py -l')
    args = parser.parse_args()

    if args.file:
        filename = args.file
        ssr_input_path = args.inputssr
        pre_input_path = args.inputpre
        output_path = args.output + filename

        logger = Logger(output_path + '_log.txt')

        try:
            p = Transformation(filename, ssr_input_path, pre_input_path)
            p.identify_actor()
            p.apply_rules()
            with open(output_path + '.transformed.txt', 'w') as file:
                obj = { "domain" : p.domain.get_name(),
                        "entity_dict" : p.domain.entity_asdict(), 
                        "relation_dict" : p.domain.relation_asdict(),
                        "behavior_dict" : p.domain.behavior_asdict()
                    }
                json.dump(obj, file, indent=2)
        except:
            logger.error(traceback.format_exc())

            # uml_filename = filename
            # uml_generated_path = os.getcwd() + '/Diagrams/'
            # try:
            #     print("Generating diagram for " + uml_generated_path + uml_filename)
            #     UML_graphic(p.class_dict, p.relationship_dict, uml_generated_path, uml_filename) 
            # except Exception as e:
            #     logger.error("Cannot generate " + uml_generated_path + uml_filename + "\n" + str(e))
            #     pass
      
    elif args.list:
        input_path = args.input
        files = os.listdir(input_path)
        f_list = set()
        pattern = '.ssr.txt'
        for f in files:
            if re.search(pattern, f):
                f_list.add(re.sub(pattern, rf"", f))
        for f in sorted(f_list):
            print(f)  

    else:
        parser.print_help()



