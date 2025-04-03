import bot_scripts as scripts
import logging, os
from config.config import *

logger = logging.getLogger(__name__)

def main(): 
    full_name = log_path + '/' + log_file_name
    if not os.path.isdir(log_path):
        try:
            os.mkdir(log_path)
        except: 
            full_name = log_file_name
    logging.basicConfig(format = log_pattern, level = log_level, filename = full_name)
    logger.info('Started')
    logger.info('Finished1')
    logger.debug( u'This is a debug message' )

if __name__ == '__main__':
    main()

