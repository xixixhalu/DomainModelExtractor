from util.logger import Logger

class File_Writer:
    def __init__(self, filename, fake_mode=False):
        self.filename = filename
        self.fake_mode = fake_mode
        self.misspelling_output_path = './output/misspelling_detect_1/' + filename
        self.preprocessing_output_path = './output/preprocessing_2/' + filename
    
    def misspelling_writer(self, input):
        if not self.fake_mode:
            with open(self.misspelling_output_path + '.corrected.txt', 'w') as outfile:
                outfile.writelines(input)
        else:
            return
    
    def misspelling_write_log(self, input, instruction):
        if not self.fake_mode:
            self.misspelling_logger = Logger(self.misspelling_output_path + '_log.txt')
            if instruction == 'info':
                self.misspelling_logger.info(input)
            elif instruction== 'warning':
                self.misspelling_logger.warning(input)
            elif instruction == 'error':
                self.misspelling_logger.error(input)
        else:
            return
    
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
