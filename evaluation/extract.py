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


def get_entity_dict(models):
    entity_dict = dict()
    id_entity_dict = dict()  # To extract Generalization Relationship needs this
    model_nodes = models.getElementsByTagName("Model")[0].childNodes
    model_nodes = extract_valid_nodes(model_nodes)
    model_children = None
    for model_node in model_nodes:
        if model_node.tagName == "ModelChildren":
            model_children = model_node
            break
    model_children_nodes = model_children.childNodes
    # get all entity nodes here
    model_children_nodes = extract_valid_nodes(model_children_nodes)
    for class_ele in model_children_nodes:
        name = class_ele.getAttribute("Name")
        id = class_ele.getAttribute("Id")
        entity_dict[name] = dict()
        entity_dict[name]["name"] = name
        id_entity_dict[id] = name
        class_ele_nodes = extract_valid_nodes(class_ele.childNodes)
        for class_ele_node in class_ele_nodes:
            # ModelChildren has the attributes of a class
            if class_ele_node.tagName != "ModelChildren": continue
            class_eles = extract_valid_nodes(class_ele_node.childNodes)
            entity_dict[name]["attribute"] = []
            for class_ele in class_eles:
                if class_ele.tagName == "Operation":
                    attribute_name = class_ele.getAttribute("Name")
                    attribute_type = "operation"
                    entity_dict[name]["attribute"].append({"name": attribute_name, "type": attribute_type})
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
                    entity_dict[name]["attribute"].append({"name": attribute_name, "type": attribute_type})
    return [entity_dict, id_entity_dict]


def get_relation_behavior_list(models, id_entity_dict):
    relation_list = []
    behavior_list = []
    # ModelChildren
    relation_container_nodes = models.getElementsByTagName("ModelRelationshipContainer")[0]
    relation_container_nodes = extract_valid_nodes(relation_container_nodes.childNodes)
    relation_container_nodes = extract_valid_nodes(relation_container_nodes[0].childNodes)
    for relation_container_node in relation_container_nodes:
        relation_nodes = extract_valid_nodes(relation_container_node.childNodes)
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
                                         , "multiplicity": [from_end_mul, to_end_mul]})
                behavior_list.append({"actor": from_end_name, "target": to_end_name, "action": action})
                # print(from_end_name, to_end_name)
            elif relation_node.tagName == "Generalization":
                from_end_name = id_entity_dict[relation_node.getAttribute("From")]
                to_end_name = id_entity_dict[relation_node.getAttribute("To")]
                relation_list.append({"source": from_end_name, "dest": to_end_name, "type": "generalization"
                                         , "multiplicity": ["1", "1"]})
    return [relation_list, behavior_list]


if __name__ == '__main__':
    input_file_paths = []
    test_data_path = "./test_data"
    test_output_path = "./test_output"
    test_data_content = os.walk(test_data_path)
    for cur_path, dirs, files in test_data_content:
        for file in files:
            input_file_paths.append("{}/{}".format(cur_path, file))
    for input_file_path in input_file_paths:
        DOMTree = xml.dom.minidom.parse(input_file_path)
        collection = DOMTree.documentElement
        models = collection.getElementsByTagName("Models")[0]
        entity_dict, id_entity_dict = get_entity_dict(models)
        relation_list, behavior_list = get_relation_behavior_list(models, id_entity_dict)
        output_file = open("{}/{}.txt".format(test_output_path, input_file_path.split("/")[-1].split(".")[0]), "w+")
        output = dict()
        output["entity_dict"] = entity_dict
        output["relation_list"] = relation_list
        output["behavior_list"] = behavior_list
        output_file.write(json.dumps(output, indent=2))
        output_file.close()
        # print(entity_dict.items())
        # print(relation_list)
        # print(behavior_list)
        print("------------------------------------------")
