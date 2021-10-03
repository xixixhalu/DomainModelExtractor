import sys
sys.path.append('../')
import re
import json
from json import JSONEncoder

from dme_ui_api.util.IS import *

# filter stop words
STOP_WORDS = {'system', 'tool', 'website'}
def S_TR1(domain):
    for entity in domain.entity_asdict():
        if entity.lower() in STOP_WORDS:
            domain.delete_entity(entity)
    for behavior in domain.behavior_asdict():
        actor = behavior['actor']
        target = behavior['target']
        if actor.lower() in STOP_WORDS:
            domain.delete_behavior(actor=actor)
        if target.lower() in STOP_WORDS:
            domain.delete_behavior(target=target)
    for relation in domain.relation_asdict():
        source = relation['source']
        dest = relation['dest']
        if source.lower() in STOP_WORDS:
            domain.delete_relation(source=source)
        if dest.lower() in STOP_WORDS:
            domain.delete_relation(dest=dest)

# reconstruct shared concepts
def S_TR2(domain):

    # Use trie tree to reconstruct the word
    class TrieNode(object):
        def __init__(self, word):
            self.word = word
            self.children = []
            self.word_finished = False
            self.counter = 1


    class TrieNodeEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__


    def add_word(root, word):
        if word == '':
            return False

        pattern = '((?<=[a-z])[A-Z]|[A-Z](?=[a-z]))'
        items = re.sub(pattern, r' \1', word).strip()
        terms = items.split(' ')

        node = root
        for t in terms:
            found_in_child = False
            for child in node.children:
                if child.word == t:
                    child.counter += 1
                    node = child
                    found_in_child = True
                    break

            if not found_in_child:
                new_node = TrieNode(t)
                node.children.append(new_node)
                node = new_node

        node.word_finished = True
        return True


    def reconstruct_word(current_node, current_word, word_map):
        if not current_node.children:
            new_word = current_word + current_node.word
            word_map[new_word] = []
        
        for child in current_node.children:
            new_word = current_word + current_node.word
            if (
                current_node.counter == 1
                or(len(current_node.children) == 1 and not current_node.word_finished)
               ):
                reconstruct_word(child, new_word, word_map)
            else:
                word_map.setdefault(new_word, []).append(reconstruct_word(child, '', {}))
        return word_map
        
    root = TrieNode('')

    # add_word(root, 'Player')
    # add_word(root, 'PlayerData')
    # add_word(root, 'PlayerValue')
    # add_word(root, 'AdminValue')
    # add_word(root, 'AdminData')    
    # add_word(root, 'Admin')
    # add_word(root, 'AdminFileOne')
    # add_word(root, 'AdminFileTwo')
    # add_word(root, 'AdminFile')
    # add_word(root, 'PlayerAddressTwo')
    # add_word(root, 'Data')
    # add_word(root, 'AdminData')
    # print(TrieNodeEncoder().encode(root))

    # After reconstruction of word, update the domain class
    relation_list = domain.get_relation()
    entity_dict = domain.get_entity()
    behavior_list = domain.get_behavior()
    entities = set(entity_dict.keys())
    entities.update(item.actor for item in behavior_list)
    entities.update(item.target for item in behavior_list)
    entities.update(item.source for item in relation_list)
    entities.update(item.dest for item in relation_list)
    for e in entities:
        add_word(root, e)
    # print(TrieNodeEncoder().encode(root))
    
    new_map = reconstruct_word(root, '', {})
    # print(new_map, len(new_map))
    # print(entities)
    
    def transform_helper(word_map, prefix, entities):
        key = list(word_map.keys())[0]
        if key not in entities:
            domain.add_entity(entity_name=key, entity_type='shared')
        domain.add_relation(source=prefix, dest=key, ass_type='aggregation')

        if not word_map[key]:
            return (prefix + key, key)
        else:
            for w in word_map[key]: 
                return transform_helper(w, prefix + key, entities)

    transform_map = []
    for key in new_map.keys():
        if key == '':
            continue
        if key not in entities:
            domain.add_entity(entity_name=key, entity_type='shared')
        for w in new_map[key]:
            transform_map.append(transform_helper(w, key, entities))
    # print(transform_map)

    for pair in transform_map:
        for r in relation_list:
            if r.source == pair[0]:
                r.source = pair[1]
            if r.dest == pair[0]:
                r.dest = pair[1]
        for b in behavior_list:
            if b.actor == pair[0]:
                b.actor = pair[1]
            if b.target == pair[0]:
                b.target = pair[1]
        for key in entity_dict.keys():
            if key == pair[0]:
                domain.add_relation(source=pair[0], dest=pair[1], ass_type='generalization')

