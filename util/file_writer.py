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
          "type": ["actor"]
          },
        },
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
