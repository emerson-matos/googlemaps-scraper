import logging
from customformater import CustomFormatter

def get_logger(logger_name = 'logger'):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler('logs/' + logger_name + '.log')
    fh.setLevel(logging.DEBUG)

    fh.setFormatter(CustomFormatter())

    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    ch.setFormatter(CustomFormatter())

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
