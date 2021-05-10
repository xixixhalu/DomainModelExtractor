import os
import sys
import traceback
import pygtrie as trie
import json
import argparse
import pandas as pd
from Parser.PosTagParser import *
from Parser.TDParser import *

# from UMLViewer import *
import re

from util.logger import Logger
global logger

from util.IS import *

from TR import *

STOP_WORDS = {'system', 'tool', 'website'}

class Transformation:
    def __init__(self, filename, ssr_input_path, pre_input_path):
        self.ssr_file_path = ssr_input_path + filename + ".ssr.txt"
        self.actor_file_path = pre_input_path + filename + ".actor.txt"
        self.meta_file_path = pre_input_path + filename + ".meta.txt"
        self.domain = ISDomain(filename)

    def transform(self, action, variables, transformation_rule):
        method_to_call = getattr(self.domain, action)

        # prepare keyword arguments
        arguments = {}
        arg_list = transformation_rule.split(',')
        for arg in arg_list:
            arg_pair = arg.strip().split('=')
            arg_pair[0] = arg_pair[0].strip()
            arg_pair[1] = re.sub(r'\W+', '', variables[arg_pair[1]]).strip()

            arguments[arg_pair[0]] = arg_pair[1]

        method_to_call(**arguments)


    def identify_actor(self):
        with open(self.actor_file_path, 'r') as f:
            line = f.readline().strip()
            while line:
                actor_list = eval(line)
                for actor_word in actor_list:
                    actor = ""
                    for word in actor_word:
                        word = re.sub(r'\W+', '', word)
                        word = word[0].upper() + word[1:]
                        actor += word
                    self.domain.add_entity(actor, "actor")
                line = f.readline().strip()
        # print(json.dumps(self.domain.entity_asdict(), indent=2))

    def identify_entity(self):
        with open(self.meta_file_path, 'r') as f:
            line = f.readline().strip()
            while line:
                entity_list = eval(line)
                for entity_word in entity_list:
                    print(entity_word[0])
                    entity = ""
                    for word in entity_word[0]:
                        word = re.sub(r'\W+', '', word)
                        word = word[0].upper() + word[1:]
                        entity += word
                    self.domain.add_entity(entity, "entity")
                line = f.readline().strip()
        # print(json.dumps(self.domain.entity_asdict(), indent=2))

    def apply_rules(self, rule_obj):
        tr_name = list(rule_obj['Rule'])
        rule_obj.set_index(["Rule"], inplace=True)

        with open(self.ssr_file_path, 'r') as f:
            data = json.loads((f.read()))

        # Iterate transformation rules
        for tr in tr_name:
            try:
                line = rule_obj.loc[tr]
            except:
                print("Error! Check the log")
                logger.error(tr + ' not found! Try the other RULEs!')
                continue
            ssr_name = line.loc['Sentence Structure'].strip()
            action = line.loc['Action'].strip()
            transformation_rule = line.loc['Transformation'].strip()
            
            # Iterate sentences matched to SSR
            for s in data[ssr_name]:
                s_index = s['Index']
                s_result = s['Result']

                # Iterate matched variables
                variables = {}
                for var, idx in s_result.items():
                    variables[var] = s_index[str(idx)]

                self.transform(action, variables, transformation_rule)

    def extra_operation(self):
        # filter stop words
        for entity in self.domain.entity_asdict():
            if entity.lower() in STOP_WORDS:
                self.domain.delete_entity(entity)
        for behavior in self.domain.behavior_asdict():
            actor = behavior['actor']
            target = behavior['target']
            if actor.lower() in STOP_WORDS:
                self.domain.delete_behavior(actor=actor)
            if target.lower() in STOP_WORDS:
                self.domain.delete_behavior(target=target)
        for relation in self.domain.relation_asdict():
            source = relation['source']
            dest = relation['dest']
            if source.lower() in STOP_WORDS:
                self.domain.delete_relation(actor=source)
            if dest.lower() in STOP_WORDS:
                self.domain.delete_relation(dest=dest)



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
    parser.add_argument('-t', '--tr', type=str, metavar='', default="./TR/TR.xlsx",
                        help='sentence structure path. Default: %(default)s')
    parser.add_argument('-l', '--list', action='store_true',
                        help='list all input files. Example: python3 rule_transforming.py -l')
    args = parser.parse_args()

    if args.file:
        filename = args.file
        ssr_input_path = args.inputssr
        pre_input_path = args.inputpre
        output_path = args.output + filename
        rule_obj = pd.read_excel(args.tr)

        logger = Logger(output_path + '_log.txt')

        try:
            p = Transformation(filename, ssr_input_path, pre_input_path)
            p.identify_actor()
            # p.identify_entity()
            p.apply_rules(rule_obj)
            p.extra_operation()
            with open(output_path + '.transformed.txt', 'w') as file:
                obj = { "domain" : p.domain.get_name(),
                        "entity_dict" : p.domain.entity_asdict(), 
                        "relation_list" : p.domain.relation_asdict(),
                        "behavior_list" : p.domain.behavior_asdict()
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
        input_path = args.inputssr
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



