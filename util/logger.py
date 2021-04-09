import logging

class Logger:

    def __init__(self, filename):
        self.baseFilename = filename
        logging.basicConfig(filename=filename, 
                            level=logging.INFO,
                            filemode='w',
                            format='%(asctime)s - %(levelname)s\n%(message)s', 
                            datefmt='%d-%b-%y %H:%M:%S')
        self.logger = logging.getLogger()

    # def debug(self, text):
    #     self.logger.debug(text)

    def info(self, text):
        self.logger.info(text)

    def warning(self, text):
        self.logger.warning(text)

    def error(self, text):
        self.logger.error(text)

    def critical(self, text):
        self.logger.critical(text)

if __name__ == '__main__':
    logger = Logger("runtime.log")
    logger.error("test")