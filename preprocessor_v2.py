import os

from adapter import *
from Parser.PosTagParser import *
from Parser.TDParser import *
from nltk.tree import Tree
import queue


# create a class to pre-process
# 1. replace I with role
# 2. combine consecutive Nouns
# 3. output another identical file


class PreProcessor:

    def __init__(self, file_path):
        self.file = open(file_path)

    def pre_process(self):
        # overwrite previous output file
        dirs = os.getcwd() + "/input_v2/"
        if not os.path.exists(dirs):
            os.makedirs(dirs)

        output = open(dirs + os.path.basename(self.file.name), "w")
        metadata = open(dirs + "meta_" + os.path.basename(self.file.name), "w")
        actors = open(dirs + "actor_" + os.path.basename(self.file.name), "w")

        line = self.file.readline().strip()
        while line:
            # print("Original sentence: ", line)
            meta = []

            # maps combined noun to the original nouns
            actor_map = {}
            act = []

            line = self.combine_nouns(line, meta, actor_map)
            line = self.replace_role(line, actor_map, act)

            print(line)


            output.write(line + "\n")
            metadata.write(meta.__str__() + "\n")
            actors.write(act.__str__() + "\n")

            # print("Meta data: ", meta)
            # print(" ")

            line = self.file.readline().strip()

        output.close()
        metadata.close()
        actors.close()

    def combine_nouns(self, line, meta, actor_map):
        noun_set = {'NN', 'NNP', 'NNS', 'NNPS'}
        nlp_output = analyze(line)
        tree = Tree.fromstring(nlp_output['sentences'][0]['parse'])
        candidates = []
        q = queue.Queue()
        q.put(tree)
        while q.qsize() != 0:
            node = q.get()
            if node._label == 'NP':
                leaves = []
                def get_leaf_node(node):
                    if isinstance(node[0], str):
                        leaves.append(node)
                    else:
                        for i in range(0, len(node)):
                            get_leaf_node(node[i])

                get_leaf_node(node)

                idx = 0
                while idx < len(leaves):
                    if leaves[idx]._label == 'JJ':
                        start = idx
                        idx += 1
                        while idx < len(leaves) and leaves[idx]._label == 'JJ':
                            idx += 1
                        jj_end = idx
                        while idx < len(leaves) and leaves[idx]._label in noun_set:
                            idx += 1
                        end = idx
                        if end == jj_end:
                            continue
                        candidates.append([leaves[i][0] for i in range(start, end)])
                    elif leaves[idx]._label in noun_set:
                        start = idx
                        while idx < len(leaves) and leaves[idx]._label in noun_set:
                            idx += 1
                        candidates.append([leaves[i][0] for i in range(start, idx)])
                    idx += 1
            else:
                for i in range(0, len(node)):
                    if not isinstance(node[i][0], str):
                        q.put(node[i])
        new_line = line
        for candidate in candidates:
            combine = ''
            for word in candidate:
                combine += word[0].upper() + word[1:]
            new_line = new_line.replace(' '.join(candidate), combine)
            if combine not in actor_map:
                actor_map[combine] = candidate
                meta.append(candidate)
        return new_line

    def replace_role(self, line, actor_map, act):
        nlp_output = analyze(line)
        noun_set = {'NN', 'NNP', 'NNS', 'NNPS'}
        tokens = [d['word'] for d in nlp_output['sentences'][0]['tokens']]
        pos_tags = [d['pos'] for d in nlp_output['sentences'][0]['tokens']]
        outputs = []
        if tokens[0] == 'As' or tokens[0] == 'as':
            if tokens[1] == 'a' or tokens[1] == 'an':
                idx = 2
            else:
                idx = 1
            while idx < len(pos_tags) and pos_tags[idx] not in noun_set:
                idx += 1
            role = tokens[idx]
            outputs.extend(tokens[idx+1:])
            if outputs[0] == ',':
                outputs = outputs[1:]

            def index(tokens, original, replace):
                for i, token in enumerate(tokens):
                    if token == original:
                        tokens[i] = replace

            self.extract_actors(role, actor_map, act)
            subjects = ['I', 'i', 'we', 'We']
            for subject in subjects:
                index(outputs, subject, role)
            pronouns = ['my']
            for pronoun in pronouns:
                index(outputs, pronoun, role + "'s")
        else:
            outputs = tokens
        res = ' '.join(outputs)
        return res

    def extract_actors(self, line, actor_map, act):
        # print("Roles sentence: ", line)
        nlp_output = analyze(line)
        if nlp_output is None:
            # print(line, ": NLP API returns None. skip!")
            return ''

        # print nlp_output
        pt = parsePosTag(nlp_output)
        # print("Roles Pos Tags: ", pt)

        # get all nouns
        nouns = set()
        if 'NN' in pt:
            for pair in pt['NN']:
                nouns.add(pair[0])
        if 'NNS' in pt:
            for pair in pt['NNS']:
                nouns.add(pair[0])
        if 'NNP' in pt:
            for pair in pt['NNP']:
                nouns.add(pair[0])
        if 'NNPS' in pt:
            for pair in pt['NNPS']:
                nouns.add(pair[0])

        # print "Unsorted nouns index in role: ", nouns
        sorted(nouns)
        # print("Sorted nouns index in role: ", nouns)

        tokens = nlp_output['sentences'][0]['tokens']
        for actor in nouns:
            actor = tokens[actor - 1]['word']
            if actor in actor_map:
                act.append(actor_map[actor])
            else:
                act.append(actor)

        # print("Actors: ", act)


if __name__ == '__main__':

    # p = PreProcessor(os.getcwd() + "/Data/input_origin/" + "test.txt")
    for year in range(2014, 2020):
        for project in range(1, 16):
            file_name = str(year) + '-USC-Project' + str(project).rjust(2, '0')
            file_path = os.getcwd() + "/Data/input_origin/" + file_name + '.txt'
            if not os.path.exists(file_path):
                continue
            print("processing " + file_path)
            p = PreProcessor(file_path)
            p.pre_process()
