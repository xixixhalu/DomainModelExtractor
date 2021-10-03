import os
import argparse
import re
import json
import traceback
from dme_ui_api.util.UMLViewer import *
from dme_ui_api.util.logger import Logger
global logger

def UML_graphic(domain_data, output_path='./output'):
    viewer = UMLViewer(domain_data['domain'])
    # print(json.dumps(domain_data['entity_dict'], indent=2))

    for k, v in domain_data['entity_dict'].items():
        entity_name = v['name']
        if re.search("\W", entity_name) != None:
            entity_name = '"' + entity_name + '"'
        if 'actor' in v['type']:
            entity_name += "<actor>"
        viewer.add_entity(entity_name)
        for attr in v['attributes']:
            attr_name = attr['name']
            if re.search("\W", attr_name) != None:
                attr_name = '"' + attr_name + '"'
            viewer.add_attribute(entity_name, attr_name)

    for behavior in domain_data['behavior_list']:
        actor = behavior['actor']
        action = behavior['action']
        target = behavior['target']
        if re.search("\W", actor) != None:
            actor = '"' + actor + '"'
        if re.search("\W", action) != None:
            action = '"' + action + '"'
        if re.search("\W", target) != None:
            target = '"' + target + '"'
        viewer.add_behavior(actor, action, parameters=behavior['para'])
        if not target == "":
            try:
                actor_attrs = [attr['name'] for attr in domain_data['entity_dict'][actor]['attributes']]
            except:
                actor_attrs = []
            r = re.compile(target, re.IGNORECASE)
            if list(filter(r.match, actor_attrs)):
                uml_asso = UMLAssociation(actor, target, "aggregation", action)
            else:
                uml_asso = UMLAssociation(actor, target, "association", action)
            viewer.add_association(uml_asso)

            
    for relation in domain_data['relation_list']:
        source = relation['source']
        dest = relation['dest']
        ass_type = relation['type']
        msg = relation['msg']
        if re.search("\W", source) != None:
            source = '"' + source + '"'
        if re.search("\W", dest) != None:
            dest = '"' + dest + '"'
        uml_asso = UMLAssociation(source, dest, ass_type, msg)
        viewer.add_association(uml_asso)         
        
    # viewer.save_to_file(path=output_path)
               
    # viewer.generate_diagram(path=output_path)
    return viewer.generate_diagram(img_format='png')
    






if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Visualization')
    parser.add_argument('-i', '--input', type=str, metavar='', default="./output/tr_process_4/",
                        help='Transformation result path. Default: %(default)s')
    parser.add_argument('-f', '--file', type=str, metavar='',
                        help='input file. Example: python3 visualizing.py -f 2014-USC-Projecct02')
    parser.add_argument('-o', '--output', type=str, metavar='', default="./output/diagram_5/",
                        help='output path. Default: %(default)s')
    parser.add_argument('-l', '--list', action='store_true',
                        help='list all input files. Example: python3 visualizing.py -l')
    args = parser.parse_args()

    if args.file:
        filename = args.file
        input_path = args.input + filename + '.transformed.txt'
        output_path = args.output + filename

        logger = Logger(output_path + '_log.txt')

        try:
            with open(input_path, 'r') as f:
                domain_data = json.loads((f.read()))
                UML_graphic(domain_data, output_path)
        except:
            print("Error! Check the log")
            logger.error(traceback.format_exc())

      
    elif args.list:
        input_path = args.input
        files = os.listdir(input_path)
        f_list = set()
        pattern = '.transformed.txt'
        for f in files:
            if re.search(pattern, f):
                f_list.add(re.sub(pattern, rf"", f))
        for f in sorted(f_list):
            print(f)  

    else:
        parser.print_help()
   
    
