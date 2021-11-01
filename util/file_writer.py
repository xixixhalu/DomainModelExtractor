from util.logger import Logger
#from logger import Logger
import json

class FileWriter:
    def __init__(self, output_path):
        self.output_path = output_path
    
    
    def write(self, input):
        if issubclass(type(input), str):
            self._write_str(input)
        elif issubclass(type(input), list):
            self._write_list(input)
        elif issubclass(type(input), dict):
            self._write_json(input)
        else:
            print('Error Input type, please check data type')
            return
            
            
    def write_log(self, input, instruction):
        logger = Logger(self.output_path)
        if instruction == 'info':
            logger.info(input)
        elif instruction== 'warning':
            logger.warning(input)
        elif instruction == 'error':
            logger.error(input)
        elif instruction == 'critical':
            logger.critical(input)
        else:
            print("Incorrect instruction")
            return
        
        
    def _write_str(self, input):
        with open(self.output_path, 'w') as outfile:
            outfile.write(input)
    
    
    def _write_list(self, input):
        lines = [line.__str__()+'\n' for line in input]
        with open(self.output_path, 'w') as outfile:
            outfile.writelines(lines)


    def _write_json(self, input):
        with open(self.output_path, 'w') as outfile:
            json.dump(input, outfile, indent=2)


class FakeWriter:
    def write(self, input):
        return
    
    def write_log(self, input, instruction):
        return
        

if __name__ == '__main__' :
    str_writer = file_writer('str_writer.txt')
    str_writer.write("abcd chsaof ascfa. hvakdchfa, sacgfa!")
    list_writer = file_writer('list_writer.txt')
    list_sample = [[['GM'], ['coach']],[['GM']],[['GM']],[],[],[],[],[['SporTech', 'B.I.', 'contractor']],[],[],[],[],[['manger'], ['manger'], ['manger'], ['manger'], ['manger'], ['manger'], ['manger'], ['manger'], ['manger'], ['manger'], ['manger'], ['manger']],[],[],[],[['customer']],[],[],[],[],[['customer'], ['customer']],[],[['SporTech', 'B.I', 'contractor'], ['SporTech', 'B.I', 'contractor']],[['soccer', 'coach']],[],[],[['soccer', 'coach']],[],[],[],[],[],[],[]]
    list_writer.write(list_sample)
    dict_writer =file_writer('dict_writer.txt')
    dict_sample = {
  "domain": "2014-USC-Project01",
  "entity_dict": {
    "User": {
      "name": "User",
      "type": [
        "actor"
      ],
      "attributes": [
        {
          "name": "thread",
          "type": "default"
        },
        {
          "name": "lifetime",
          "type": "default"
        },
        {
          "name": "watPoint",
          "type": "default"
        },
        {
          "name": "pointBalance",
          "type": "default"
        },
        {
          "name": "progress",
          "type": "default"
        },
        {
          "name": "point",
          "type": "default"
        },
        {
          "name": "peer",
          "type": "default"
        },
        {
          "name": "profile",
          "type": "default"
        },
        {
          "name": "experience",
          "type": "default"
        }
      ]
    },
    "Administrator": {
      "name": "Administrator",
      "type": [
        "actor"
      ],
      "attributes": []
    },
    "Maintainer": {
      "name": "Maintainer",
      "type": [
        "actor"
      ],
      "attributes": []
    },
    "Balance": {
      "name": "Balance",
      "type": [
        "shared"
      ],
      "attributes": []
    },
    "Store": {
      "name": "Store",
      "type": [
        "shared"
      ],
      "attributes": []
    },
    "Card": {
      "name": "Card",
      "type": [
        "shared"
      ],
      "attributes": []
    },
    "Wat": {
      "name": "Wat",
      "type": [
        "shared"
      ],
      "attributes": []
    },
    "System": {
      "name": "System",
      "type": [
        "shared"
      ],
      "attributes": []
    }
  },
  "relation_list": [
    {
      "source": "User",
      "dest": "Information",
      "type": "association",
      "msg": "supported_by",
      "multiplicity": [
        "1",
        "1"
      ],
      "para": []
    },
    {
      "source": "Point",
      "dest": "Balance",
      "type": "aggregation",
      "msg": "",
      "multiplicity": [
        "1",
        "1"
      ],
      "para": []
    },
    {
      "source": "Wat",
      "dest": "Point",
      "type": "aggregation",
      "msg": "",
      "multiplicity": [
        "1",
        "1"
      ],
      "para": []
    },
    {
      "source": "Product",
      "dest": "Store",
      "type": "association",
      "msg": "to",
      "multiplicity": [
        "1",
        "1"
      ],
      "para": []
    },
    {
      "source": "Gift",
      "dest": "Store",
      "type": "aggregation",
      "msg": "",
      "multiplicity": [
        "1",
        "1"
      ],
      "para": []
    },
    {
      "source": "Gift",
      "dest": "Card",
      "type": "aggregation",
      "msg": "",
      "multiplicity": [
        "1",
        "1"
      ],
      "para": []
    },
    {
      "source": "Wat",
      "dest": "System",
      "type": "aggregation",
      "msg": "",
      "multiplicity": [
        "1",
        "1"
      ],
      "para": []
    },
    {
      "source": "User",
      "dest": "Peer",
      "type": "association",
      "msg": "supported_by",
      "multiplicity": [
        "1",
        "1"
      ],
      "para": []
    }
  ],
  "behavior_list": [
    {
      "actor": "User",
      "action": "mark",
      "target": "Comment",
      "para": []
    },
    {
      "actor": "Maintainer",
      "action": "manage",
      "target": "Comment",
      "para": []
    },
    {
      "actor": "User",
      "action": "view",
      "target": "Lifetime",
      "para": []
    },
    {
      "actor": "User",
      "action": "use",
      "target": "Point",
      "para": []
    },
    {
      "actor": "User",
      "action": "redeem",
      "target": "Point",
      "para": []
    },
    {
      "actor": "User",
      "action": "receive",
      "target": "Card",
      "para": []
    },
    {
      "actor": "Maintainer",
      "action": "manage",
      "target": "Thread",
      "para": []
    },
    {
      "actor": "Card",
      "action": "use",
      "target": "Point",
      "para": []
    },
    {
      "actor": "User",
      "action": "get",
      "target": "NewsFeed",
      "para": []
    },
    {
      "actor": "User",
      "action": "like",
      "target": "Answer",
      "para": []
    },
    {
      "actor": "User",
      "action": "start",
      "target": "Thread",
      "para": []
    },
    {
      "actor": "User",
      "action": "redeem",
      "target": "Gift",
      "para": []
    },
    {
      "actor": "User",
      "action": "view",
      "target": "Page",
      "para": []
    },
    {
      "actor": "User",
      "action": "see",
      "target": "Information",
      "para": []
    },
    {
      "actor": "User",
      "action": "view",
      "target": "Point",
      "para": []
    },
    {
      "actor": "User",
      "action": "delete",
      "target": "Post",
      "para": []
    },
    {
      "actor": "Detail",
      "action": "create",
      "target": "System",
      "para": []
    },
    {
      "actor": "User",
      "action": "overpenalize",
      "target": "",
      "para": []
    },
    {
      "actor": "Maintainer",
      "action": "entice",
      "target": "User",
      "para": []
    },
    {
      "actor": "Detail",
      "action": "create",
      "target": "Event",
      "para": []
    },
    {
      "actor": "User",
      "action": "answer",
      "target": "Question",
      "para": []
    },
    {
      "actor": "User",
      "action": "view",
      "target": "Leaderboard",
      "para": []
    },
    {
      "actor": "User",
      "action": "report",
      "target": "Thread",
      "para": []
    },
    {
      "actor": "User",
      "action": "select",
      "target": "",
      "para": []
    },
    {
      "actor": "Gift",
      "action": "use",
      "target": "Point",
      "para": []
    },
    {
      "actor": "User",
      "action": "gauge",
      "target": "",
      "para": []
    },
    {
      "actor": "User",
      "action": "see",
      "target": "Point",
      "para": []
    },
    {
      "actor": "User",
      "action": "post",
      "target": "",
      "para": []
    },
    {
      "actor": "User",
      "action": "view",
      "target": "Profile",
      "para": []
    },
    {
      "actor": "Point",
      "action": "redeem",
      "target": "Item",
      "para": []
    },
    {
      "actor": "Maintainer",
      "action": "edit",
      "target": "Event",
      "para": []
    },
    {
      "actor": "Information",
      "action": "highlight",
      "target": "",
      "para": []
    },
    {
      "actor": "User",
      "action": "compare",
      "target": "Point",
      "para": []
    },
    {
      "actor": "Maintainer",
      "action": "add",
      "target": "Card",
      "para": []
    },
    {
      "actor": "User",
      "action": "delete",
      "target": "Thread",
      "para": []
    },
    {
      "actor": "User",
      "action": "see",
      "target": "",
      "para": []
    },
    {
      "actor": "User",
      "action": "start",
      "target": "",
      "para": []
    },
    {
      "actor": "Maintainer",
      "action": "add",
      "target": "Product",
      "para": []
    },
    {
      "actor": "User",
      "action": "edit",
      "target": "",
      "para": []
    },
    {
      "actor": "User",
      "action": "join",
      "target": "",
      "para": []
    },
    {
      "actor": "User",
      "action": "view",
      "target": "Balance",
      "para": []
    },
    {
      "actor": "User",
      "action": "search",
      "target": "Forum",
      "para": []
    },
    {
      "actor": "User",
      "action": "post",
      "target": "Question",
      "para": []
    },
    {
      "actor": "User",
      "action": "update",
      "target": "Profile",
      "para": []
    },
    {
      "actor": "User",
      "action": "gauge",
      "target": "Credibility",
      "para": []
    },
    {
      "actor": "User",
      "action": "dislike",
      "target": "Answer",
      "para": []
    },
    {
      "actor": "Trash",
      "action": "degrade",
      "target": "Quality",
      "para": []
    },
    {
      "actor": "User",
      "action": "see",
      "target": "Answer",
      "para": []
    },
    {
      "actor": "Maintainer",
      "action": "create",
      "target": "Event",
      "para": []
    },
    {
      "actor": "Stay",
      "action": "engage",
      "target": "",
      "para": []
    },
    {
      "actor": "User",
      "action": "view",
      "target": "Thread",
      "para": []
    },
    {
      "actor": "Balance",
      "action": "drop",
      "target": "",
      "para": []
    },
    {
      "actor": "User",
      "action": "track",
      "target": "Point",
      "para": []
    },
    {
      "actor": "Maintainer",
      "action": "edit",
      "target": "Detail",
      "para": []
    },
    {
      "actor": "Administrator",
      "action": "pin",
      "target": "Thread",
      "para": []
    },
    {
      "actor": "User",
      "action": "track",
      "target": "Progress",
      "para": []
    },
    {
      "actor": "User",
      "action": "view",
      "target": "Semester",
      "para": []
    }
  ]
}
    dict_writer.write(dict_sample)

'''
#api
misspelling.py => input -> output

4step
->input (filename)
preprocessing
ssr_matching
rule_transforming_output_path("")
visiz



class file_writer:
    def __init__(self, output_path):
        
    def write(input):
        type = type(input)
        if list str, json:
        else:
        print errror
        return
    
    def write_log(input, instr):
        logger = Logger(self.output_path)
        if instr == 'info':
            self.logger.info(input)
            
    def write_str(input):
            type(input)
            if not str: print() return
            writeline()
        elif type = list:
            for line in list:
                line.strip() + '\n'
            writelines()
        elif type = dict:
            json.dump()
            
        open(file)
            writeline(input)
    def write_List()
        
    def write_json()
class fake_writer:
    def __init__(self):
        return
    def write(Input):
        return
    def write_log()
        


# misspelling.py
    a = file_writer(./output/misspelling_detect_1/')')

# preprocessing.py
    logger = file_writer('./output/preprocessing_2/'+filename+'_log.txt')
    func_writer = file_writer('./output/preprocessing_2/'+filename+'.func.txt')
    self.outputpath =
    non_func_wr
    meta
    actro
    preprocessing()

class File_Writer:
    def __init__(self, filename, fake_mode=False):
        self.filename = filename
        self.fake_mode = fake_mode
        self.misspelling_output_path = './output/misspelling_detect_1/' + filename
        self.preprocessing_output_path = './output/preprocessing_2/' + filename
        self.rule_transforming_output_path = './output/tr_process_4/' + filename
    
    def write(self, input, type):
        if not self.fake_mode:
            if type == 'func':
                with open(self.preprocessing_output_path + '.func.txt', 'w') as outfile:
                    outfile.writelines(input)
            elif type == 'nonfunc':
                with open(self.preprocessing_output_path + '.nonfunc.txt', 'w') as outfile:
                    outfile.writelines(input)
            elif type == 'meta':
                with open(self.preprocessing_output_path + '.meta.txt', 'w') as outfile:
                    outfile.writelines(input)
            elif type == 'acts':
                with open(self.preprocessing_output_path + '.actor.txt', 'w') as outfile:
                    outfile.writelines(input)
            elif type == 'misspelling':
                with open(self.misspelling_output_path + '.corrected.txt', 'w') as outfile:
                    outfile.writelines(input)
        else:
            return
    
    def write_log(self, input, type, instruction):
        if not self.fake_mode:
            if type == 'misspelling':
                logger = Logger(self.misspelling_output_path + '_log.txt')
            elif type == 'preprocessing':
                logger = Logger(self.preprocessing_output_path + '_log.txt')
            elif type == 'rule_transforming':
                logger = Logger(self.rule_transforming_output_path + '_log.txt')
            else:
                return
            if instruction == 'info':
                logger.info(input)
            elif instruction== 'warning':
                logger.warning(input)
            elif instruction == 'error':
                logger.error(input)
        else:
            return
    
    def write_json(self, input, type):
        if not self.fake_mode:
            if type == 'rule_transforming':
                with open(self.rule_transforming_output_path + '.transformed.txt', 'w') as file:
                    json.dump(input, file, indent=2)
            else:
                return
        else:
            return
'''
