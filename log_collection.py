import logging


class logCollection(object):
    def __init__(self, filename='logfile.log'):
        self.filename = filename
        logging.basicConfig(filename=filename, format='%(asctime)s %(message)s', filemode='w')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)


