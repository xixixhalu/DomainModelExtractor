#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
from UMLViewer import *
from tr_process import *
import re
import pickle


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
        
        
        
        
    #viewer.save_to_file(path=filepath+"./")
               
    viewer.generate_diagram(path=filepath+"./")
    #viewer.generate_diagram(path=filepath+"/")
    






if __name__ == '__main__':
    for year in range(2014,2020):
        for project in range(1,16):
            filename=str(year)+'-USC-Project' + str(project).rjust(2,'0')
            filepath=os.getcwd() + '/Data/output_origin_trprocess_v2/%sResult.json'%filename
            #print(filepath)
            if not os.path.exists(filepath):
                break
            else:
                with open(filepath,'rb') as file:
                  class_dict,relationship_dict=pickle.load(file)
                file.close()  
                UML_graphic(class_dict, relationship_dict)
   
    
