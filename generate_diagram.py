#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
from UMLViewer import *
from tr_process import *
import re


def UML_graphic(class_dict, relationship_dict):
    viewer = UMLViewer()

    for className in class_dict:
        c = className
        if re.search("/W", c) != None:
            c = '"' + c + '"'
        for attr in class_dict[className]["Attribute"]:
            if re.search("\W", attr) != None:
                attr = '"' + attr + '"'
            viewer.add_attribute(c, attr)
        for behavior in class_dict[className]["Behavior"]:
            para=class_dict[className]["Behavior"][behavior]
            if re.search("\W", behavior) != None:
                behavior = '"' + behavior + '"'
            viewer.add_behavior(c, behavior, parameters=para)
            
    for rel_name in relationship_dict:
        for relationship in relationship_dict[rel_name]:
            if len(relationship[0])>1 and len(relationship[1])>1:
                if re.search("\W",relationship[0]) != None:
                    relationship[0] = '"' + relationship[0] + '"'
                if re.search("\W",relationship[1]) != None:
                    relationship[1] = '"' + relationship[1] + '"'
                uml_asso = UMLAssociation(relationship[0], relationship[1],rel_name)
                viewer.add_association(uml_asso)            
        
        
        
        
    #viewer.save_to_file(path="./")
    viewer.generate_diagram(path="./")






if __name__ == '__main__':
    print(os.getcwd() + "/Data/input_v2/" + "2014-USC-Project02.txt")
    p = TransformationRules(os.getcwd() + "/Data/input_v2/" + "2014-USC-Project02.txt")
    p.apply_rules()
    
    print ("Classed with Attributes: "+str(p.class_dict))
    print ("Relationships with parent class & child class: "+str(p.relationship_dict))
    
    UML_graphic(p.class_dict, p.relationship_dict)
    
