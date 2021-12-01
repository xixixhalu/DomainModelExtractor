import json
import os
from xml.dom.minidom import parse
import xml.dom.minidom

ELEMENT_NODE = 1


# Filter Text Nodes
# When Element get its childNodes, there may be some unnecessary
# Text Nodes for a line feed
def extract_valid_nodes(node_list):
    ans = []
    for node in node_list:
        if node.nodeType == ELEMENT_NODE:
            ans.append(node)
    return ans
def find_model_children_tag(nodes):
    model_children = None
    for model_node in nodes:
        if model_node.tagName == "ModelChildren":
            model_children = model_node
            break
    return model_children
def extract_class_or_package(nodes, class_nodes):
    for node in nodes:
        # There is a tag <NARY>, <InstanceSpecification> and <Collaboration> indicating a class
        if node.tagName == "Class" or node.tagName == "NARY" or node.tagName == "InstanceSpecification" or node.tagName == "Collaboration":
            class_nodes.append(node)
        if node.tagName == "Package":
            extract_class_from_package(node, class_nodes)

def extract_class_from_package(package_node, model_children_nodes):
    package_child_nodes = extract_valid_nodes(package_node.childNodes)
    model_children = find_model_children_tag(package_child_nodes)
    model_children_child_nodes = extract_valid_nodes(model_children.childNodes)
    for model_children_child_node in model_children_child_nodes:
        model_children_nodes.append(model_children_child_node)

def get_entity_dict_and_behavior_list(models):
    entity_dict = dict()
    behavior_list = list()
    id_entity_dict = dict()  # To extract Generalization Relationship needs this
    models_child_nodes = extract_valid_nodes(models.childNodes)
    class_nodes = []
    extract_class_or_package(models_child_nodes, class_nodes)
    # for model_node in models_child_nodes:
    #     # There is a tag <NARY> indicating a class
    #     if model_node.tagName == "Class" or model_node.tagName == "NARY":
    #         class_nodes.append(model_node)
    #     if model_node.tagName == "Package":
    #         extract_class_from_package(model_node, class_nodes)
    model_nodes = models.getElementsByTagName("Model")
    if len(model_nodes) != 0:
        model_nodes = model_nodes[0].childNodes
        model_nodes = extract_valid_nodes(model_nodes)
        model_children = find_model_children_tag(model_nodes)
        # for model_node in model_nodes:
        #     if model_node.tagName == "ModelChildren":
        #         model_children = model_node
        #         break
        model_children_nodes = model_children.childNodes
        # get all entity nodes here
        model_children_nodes = extract_valid_nodes(model_children_nodes)
        extract_class_or_package(model_children_nodes, class_nodes)
    else:
        model_nodes = models.childNodes
        model_nodes = extract_valid_nodes(model_nodes)
        extract_class_or_package(model_nodes, class_nodes)
        # for model_node in model_nodes:
        #     # There is a tag <NARY> indicating a class
        #     if model_node.tagName == "Class" or model_node.tagName == "NARY":
        #         class_nodes.append(model_node)
        #     if model_node.tagName == "Package":
        #         extract_class_from_package(model_node, class_nodes)
    for class_ele in class_nodes:
        name = class_ele.getAttribute("Name")
        id = class_ele.getAttribute("Id")
        entity_dict[name] = dict()
        entity_dict[name]["name"] = name
        entity_dict[name]["type"] = []
        entity_dict[name]["attributes"] = []
        id_entity_dict[id] = name
        class_ele_nodes = extract_valid_nodes(class_ele.childNodes)
        for class_ele_node in class_ele_nodes:
            # ModelChildren has the attributes of a class
            if class_ele_node.tagName != "ModelChildren": continue
            class_eles = extract_valid_nodes(class_ele_node.childNodes)
            for class_ele in class_eles:
                id_entity_dict[class_ele.getAttribute("Id")] = name
                if class_ele.tagName == "Operation":
                    operation = class_ele.getAttribute("Name")
                    behavior_list.append({"actor": name, "target": "", "action": operation, "para": []})
                    # attribute_type = "operation"
                    # entity_dict[name]["attributes"].append({"name": attribute_name, "type": attribute_type})
                elif class_ele.tagName == "Attribute":
                    attribute_name = class_ele.getAttribute("Name")
                    attribute_type = class_ele.getElementsByTagName("Type")
                    # no determined type for the attribute
                    if len(attribute_type) == 0:
                        attribute_type = "default"
                    # has a determined type
                    else:
                        attribute_type = extract_valid_nodes(attribute_type[0].childNodes)
                        attribute_type = attribute_type[0].getAttribute("Name")
                    entity_dict[name]["attributes"].append({"name": attribute_name, "type": attribute_type})
    return [entity_dict, id_entity_dict, behavior_list]


def get_relation_list(models, id_entity_dict):
    relation_list = []
    # behavior_list = []
    # ModelChildren
    relation_container_nodes = models.getElementsByTagName("ModelRelationshipContainer")
    if len(relation_container_nodes) == 0: return relation_list
    relation_container_nodes = extract_valid_nodes(relation_container_nodes[0].childNodes)
    relation_container_nodes = extract_valid_nodes(relation_container_nodes[0].childNodes)
    for relation_container_node in relation_container_nodes:
        relation_nodes = extract_valid_nodes(relation_container_node.childNodes)
        if len(relation_nodes) == 0:
            continue
        relation_nodes = extract_valid_nodes(relation_nodes[0].childNodes)
        # get relation nodes here
        for relation_node in relation_nodes:
            if relation_node.tagName == "Association":
                action = ""
                if relation_node.hasAttribute("Name"):
                    action = relation_node.getAttribute("Name")
                relation_type = ""
                from_end_node = relation_node.getElementsByTagName("FromEnd")[0] \
                    .getElementsByTagName("AssociationEnd")[0]
                aggregation_kind = from_end_node.getAttribute("AggregationKind")
                if aggregation_kind == "None":
                    relation_type = "association"
                elif aggregation_kind == "Composited":
                    relation_type = "composition"
                elif aggregation_kind == "Shared":
                    relation_type = "aggregation"
                from_end_mul = from_end_node.getAttribute("Multiplicity")
                from_end_name = id_entity_dict[from_end_node.getAttribute("EndModelElement")]
                to_end_node = relation_node.getElementsByTagName("ToEnd")[0] \
                    .getElementsByTagName("AssociationEnd")[0]
                to_end_mul = to_end_node.getAttribute("Multiplicity")
                to_end_name = id_entity_dict[to_end_node.getAttribute("EndModelElement")]
                relation_list.append({"source": from_end_name, "dest": to_end_name, "type": relation_type
                                         , "multiplicity": [from_end_mul, to_end_mul], "para": [], "msg": action})
                # behavior_list.append({"actor": from_end_name, "target": to_end_name, "action": action, "para": []})
                # print(from_end_name, to_end_name)
            elif relation_node.tagName == "Generalization":
                from_end_name = id_entity_dict[relation_node.getAttribute("From")]
                to_end_name = id_entity_dict[relation_node.getAttribute("To")]
                relation_list.append({"source": from_end_name, "dest": to_end_name, "type": "generalization"
                                         , "multiplicity": ["1", "1"], "para": [], "msg": ""})
            # we temporarily regard <Dependency> as <Association>
            elif relation_node.tagName == "Dependency":
                from_end_name = id_entity_dict[relation_node.getAttribute("From")]
                to_end_name = id_entity_dict[relation_node.getAttribute("To")]
                message = ""
                if relation_node.hasAttribute("Name"):
                    message = relation_node.getAttribute("Name")
                relation_list.append({"source": from_end_name, "dest": to_end_name, "type": "association"
                                         , "multiplicity": ["1", "1"], "para": [], "msg": message})
            # we temporarily regard <Realization> as the reverse of <Generalization>
            elif relation_node.tagName == "Realization":
                from_end_name = id_entity_dict[relation_node.getAttribute("From")]
                to_end_name = id_entity_dict[relation_node.getAttribute("To")]
                message = ""
                if relation_node.hasAttribute("Name"):
                    message = relation_node.getAttribute("Name")
                relation_list.append({"source": from_end_name, "dest": to_end_name, "type": "generalization"
                                     , "multiplicity": ["1", "1"], "para": [], "msg": message})
    # return [relation_list, behavior_list]
    return relation_list


if __name__ == '__main__':
    input_file_paths = []
    test_data_path = "./test_data"
    # test_data_path = "./error_data"
    test_output_path = "./test_output"
    # black_list = ["Jin_Maiqi_Team05_HW3.xml", "Li_Xingrui_Team11_HW3.xml",
    #               "Nguyen_Patrick_Team06_HW3.xml", "Osborne_Philip_Team04_HW3.xml", "Reddy_Erin_Team03_HW3.xml"
    #               , "Wu_Zhijie_Team12_HW3.xml", "XU_BOYU_Team7_HW3.xml", "Yingjie_Shen_HW3_Team_12.xml"]
    black_list = ["Jin_Maiqi_Team05_HW3.xml", "Osborne_Philip_Team04_HW3.xml", "Liao_Yuan_Team11_HW3.xml", "Nguyen_Patrick_Team06_HW3.xml"]
    test_data_content = os.walk(test_data_path)
    for cur_path, dirs, files in test_data_content:
        for file in files:
            if file in black_list: continue
            input_file_paths.append("{}/{}".format(cur_path, file))
    for input_file_path in input_file_paths:
        DOMTree = xml.dom.minidom.parse(input_file_path)
        collection = DOMTree.documentElement
        models = collection.getElementsByTagName("Models")[0]
        entity_dict, id_entity_dict, behavior_list = get_entity_dict_and_behavior_list(models)
        relation_list= get_relation_list(models, id_entity_dict)
        output_file = open("{}/{}.transformed.txt".format(test_output_path, input_file_path.split("/")[-1].split(".")[0]), "w+")
        output = dict()
        output["domain"] = input_file_path.split("/")[-1].split(".")[0]
        output["entity_dict"] = entity_dict
        output["relation_list"] = relation_list
        output["behavior_list"] = behavior_list
        output_file.write(json.dumps(output, indent=2))
        output_file.close()
        # print(entity_dict.items())
        # print(relation_list)
        # print(behavior_list)
        print("{} succeed".format(input_file_path))
