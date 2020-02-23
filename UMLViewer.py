import sys
sys.path.append('../')
from utilities.file_op import fileOps
import subprocess

class UMLEntity:
    def __init__(self, entity_name):
        self.__header = 'class ' + entity_name + ' {\n'
        self.__footer = '}\n'
        self.__content = ''
    def add_attribute(self, attribute_name, attribute_type='string'):
        self.__content += '\t' + attribute_name + ' : ' + attribute_type + '\n'

    def add_behavior(self, behavior_name):
        self.__content += '\t' + behavior_name + '()' + '\n'

    def output(self):
        return self.__header + self.__content + self.__footer

class UMLAssociation:
    def __init__(self, entity_one, entity_two, association_type='association', multiplicity='one_to_one'):
        self.__entity_one = entity_one
        self.__entity_two = entity_two
        self.__association_type = association_type
        self.__multiplicity = multiplicity

    def set_assocciation_type(self, association_type):
        self.__association_type = association_type

    def set_multiplicity(self, multiplicity):
        self.__multiplicity = multiplicity

    def association(self, association_type='association', multiplicity='one_to_one'):
        type_switcher = {
            "association": " -- ",
            "generalization": " <|-- ",
            "composition": " *-- ",
            "aggregation": " o-- "
        }
        if not association_type in type_switcher:
            result =  " -- "
        else:
            result = type_switcher[association_type]

        multiplicity_switcher = {
            "one_to_one": ' "1"' + result + '"1" ',
            "one_to_many": ' "1"' + result + '"*" ',
            "many_to_one": ' "*"' + result + '"1" ',
            "many_to_many": ' "*"' + result + '"*" ',
        }
        if not multiplicity in multiplicity_switcher:
            result = result #' "1"' + result + '"1" '
        else:
            result = multiplicity_switcher[multiplicity]
        return result


    def output(self):
        return self.__entity_two + self.association(self.__association_type, self.__multiplicity) + self.__entity_one + '\n'
        
class UMLViewer:

    def __init__(self, title='diagram', hideCircle=True):
        self.__title = title
        self.__header = '@startuml\n'
        if hideCircle is True:
            self.__header += 'hide circle\n'
        self.__footer = '\n@enduml'
        self.__content = ''
        self.__association_set = set()
        self.__entity_map = {}
    
    def add_entity(self, entity_name):
        entity = UMLEntity(entity_name)
        self.__entity_map[entity_name] = entity
        return entity

    def add_attribute(self, entity_name, attribute_name, attribute_type='string'):
        if not entity_name in self.__entity_map:
            self.add_entity(entity_name)
        self.__entity_map[entity_name].add_attribute(attribute_name, attribute_type)

    def add_behavior(self, entity_name, behavior_name, return_type=[], parameters=[]):
        if not entity_name in self.__entity_map:
            self.add_entity(entity_name)
        self.__entity_map[entity_name].add_behavior(behavior_name)

    # Bo: deprecated
    # def add_association(self, entity_one, entity_two, attribute_type='association', multiplicity='one_to_one'):
    #     association = UMLAssociation(entity_one, entity_two, attribute_type, multiplicity)
    #     self.__association_set.add(association)

    def add_association(self, association):
        if isinstance(association, UMLAssociation):
            self.__association_set.add(association)
            
    def output(self):
        for key, value in self.__entity_map.items():
            self.__content += value.output()

        for item in self.__association_set:
            self.__content += item.output()

        return self.__header + self.__content + self.__footer

    def title(self):
        return self.__title

    def save_to_file(self, path):
        with fileOps.safe_open_w(path + self.__title + '.txt') as o:
            o.write(self.output())

    def generate_diagram(self, path, format='svg'):
        file_path = path + '/' + self.__title + '.txt'
        with fileOps.safe_open_w(file_path) as o:
            o.write(self.output())
        # Bo: TODO: add more format support
        subprocess.call(['plantweb',file_path])
        subprocess.call(['mv', self.__title + '.' + format, path + '/' + self.__title + '.' + format])
        # fileOps.safe_delete_file(file_path)

if __name__ == '__main__':
    viewer = UMLViewer()
    viewer.add_attribute("test1", "first_name")
    viewer.add_attribute("test2", "last_name")

    viewer.add_association("test1", "test2")

    viewer.save_to_file(path="./")
