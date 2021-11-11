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
from util.file_writer import FileWriter, FakeWriter
global logger

from util.IS import *

from TR.special_TR import *


class Transformation:
    def __init__(self, actors, meta, ssr, writer, logger, domain_name="new_domain"):
#        self.ssr_file_path = ssr_input_path + filename + ".ssr.txt"
#        self.actor_file_path = pre_input_path + filename + ".actor.txt"
#        self.meta_file_path = pre_input_path + filename + ".meta.txt"
        self.actors = actors
        self.meta = meta
        self.ssr = ssr
        self.writer = writer
        self.logger = logger
        self.domain = ISDomain(domain_name)

    def transform(self, action, variables, transformation_rule):
        method_to_call = getattr(self.domain, action)
        # prepare keyword arguments
        arguments = {}
        arg_list = transformation_rule.split(',')
        for arg in arg_list:
            arg_pair = arg.strip().split('=')
            arg_pair[0] = arg_pair[0].strip()
            arg = ''
            # print(method_to_call.__name__)
            if re.search("\"", arg_pair[1]):
                arg = re.sub(r"\"", '', arg_pair[1]).strip()
            else:
                arg = '_'.join([re.sub(r'\W+', '', variables[i]).strip() for i in str(arg_pair[1])])
            # arg_pair[1] = re.sub(r'\W+', '', variables[arg_pair[1]]).strip()

            # arguments[arg_pair[0]] = arg_pair[1]
            arguments[arg_pair[0]] = arg

        method_to_call(**arguments)


    def identify_actor(self):
#        with open(self.actor_file_path, 'r') as f:
#            line = f.readline().strip()
#            while line:
        for line in self.actors:
                actor_list = eval(str(line))
                for actor_word in actor_list:
                    actor = ""
                    for word in actor_word:
                        word = re.sub(r'\W+', '', word)
                        word = word[0].upper() + word[1:]
                        actor += word
                    self.domain.add_entity(actor, "actor")
#                line = f.readline().strip()
        # print(json.dumps(self.domain.entity_asdict(), indent=2))

    def identify_entity(self):
#        with open(self.meta_file_path, 'r') as f:
#            line = f.readline().strip()
#            while line:
        for line in self.meta:
                entity_list = eval(str(line))
                for entity_word in entity_list:
                    entity = ""
                    for word in entity_word[0]:
                        word = re.sub(r'\W+', '', word)
                        word = word[0].upper() + word[1:]
                        entity += word
                    self.domain.add_entity(entity, "entity")
#                line = f.readline().strip()
        # print(json.dumps(self.domain.entity_asdict(), indent=2))

    def apply_rules(self, rule_obj):
        tr_name = list(rule_obj['Rule'])
        rule_obj.set_index(["Rule"], inplace=True)

#        with open(self.ssr_file_path, 'r') as f:
#            data = json.loads((f.read()))

        # Iterate transformation rules
        for tr in tr_name:
            if str(tr) == 'nan':
                continue
            try:
                line = rule_obj.loc[tr]
                ssr_name = line.loc['Sentence Structure'].strip()
                action = line.loc['Action'].strip()
                transformation_rule = line.loc['Transformation'].strip()

                # Iterate sentences matched to SSR
                for s in self.ssr[ssr_name]:
                    s_index = s['Index']
                    s_result = s['Result']
                    # Iterate matched variables
                    variables = {}
                    for var, idx in s_result.items():
                        word = s_index[str(idx)]
                        r = re.compile("^" + re.sub(r'\W+', '', word) + "$", re.IGNORECASE)
                        rst_list = list(filter(r.match, list(self.domain.entity_asdict().keys())))
                        if rst_list:
                            variables[var] = rst_list[0]
                        else:
                            variables[var] = s_index[str(idx)]
                    self.transform(action, variables, transformation_rule)
            except:
                # print("Error! Check the log")
                self.logger.write_log(sys.exc_info()[0],'error')
                continue
            

    def run(self, transforming_rule="./TR/TR.xlsx"):
            rule_obj = pd.read_excel(transforming_rule)
            obj = { "domain" : '',
                    "entity_dict" : {},
                    "relation_list" : [],
                    "behavior_list" : []
            }
        try:
            self.identify_actor()
            # p.identify_entity()
            self.apply_rules(rule_obj)
            self.extra_operation()
            obj['domain'] = self.domain.get_name()
            obj['entity_dict'] = self.domain.entity_asdict()
            obj['relation_list'] = self.domain.relation_asdict()
            obj['behavior_list'] = self.domain.behavior_asdict()
            self.writer.write(obj)
        except:
            self.logger.write_log(traceback.format_exc(), 'error')
        
            return obj
            
            
    def extra_operation(self):
        S_TR1(self.domain)
        S_TR2(self.domain)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Rule Transformation')
    parser.add_argument('-s', '--inputssr', type=str, metavar='', default="./output/ssr_match_3/",
                        help='SSR result path. Default: %(default)s')
    parser.add_argument('-p', '--inputpre', type=str, metavar='', default="./output/preprocessing_2/",
                        help='Preprocessing result path. Default: %(default)s')
    parser.add_argument('-f', '--file', type=str, metavar='',
                        help='input file. Example: python3 rule_transforming.py -f 2014-USC-Project02')
    parser.add_argument('-o', '--output', type=str, metavar='', default="./output/tr_process_4/",
                        help='output path. Default: %(default)s')
    parser.add_argument('-t', '--tr', type=str, metavar='', default="./TR/TR.xlsx",
                        help='sentence structure path. Default: %(default)s')
    parser.add_argument('-l', '--list', action='store_true',
                        help='list all input files. Example: python3 rule_transforming.py -l')
    parser.add_argument('-api', '--api_mode', action='store_true', help='api mode - no ouput to files')
    args = parser.parse_args()

    if args.file:
        filename = args.file
        ssr_input_path = args.inputssr
        pre_input_path = args.inputpre
        output_path = args.output + filename
        api_mode = args.api_mode
        transforming_rule = args.tr
        actors = meta = []
        ssr = {}
        with open(pre_input_path + filename + ".actor.txt", 'r') as f:
            actors = f.readlines()
        with open(pre_input_path + filename + ".meta.txt", 'r') as f:
            meta = f.readlines()
        with open(ssr_input_path + filename + ".ssr.txt", 'r') as f:
            ssr = json.loads((f.read()))
        
        if api_mode:
            transform_writer = FakeWriter()
            logger = FakeWriter()
            transformer = Transformation(actors=actors, meta=meta, ssr=ssr, writer=transform_writer, logger=logger)
        else:
            transform_writer = FileWriter(output_path + '.transformed.txt')
            logger = FileWriter(output_path + '_log.txt')
            transformer = Transformation(actors=actors, meta=meta, ssr=ssr, writer=transform_writer, logger=logger, domain_name=filename)
    
        transformed_obj = transformer.run(transforming_rule=transforming_rule)
#        print(transformed_obj)
        
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



