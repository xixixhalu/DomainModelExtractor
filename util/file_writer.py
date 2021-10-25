from util.logger import Logger

class File_Writer:
    def __init__(self, filename, fake_mode=False):
        self.filename = filename
        self.fake_mode = fake_mode
        self.misspelling_output_path = './output/misspelling_detect_1/' + filename
    
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
        else:
            return
