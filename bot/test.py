import bot_scripts as scripts
import logging, os, requests
from config.config import *
from bot_config import token_telegram, token_vk, group_id, channel_id 

logger = logging.getLogger(__name__)
tg_url = "https://api.telegram.org/bot" + token_telegram

# def main(): 
#     full_name = log_path + '/' + log_file_name
#     if not os.path.isdir(log_path):
#         try:
#             os.mkdir(log_path)
#         except: 
#             full_name = log_file_name
#     logging.basicConfig(format = log_pattern, level = log_level, filename = full_name)
#     logger.info('Started')
#     logger.info('Finished1')
#     logger.debug( u'This is a debug message' )

def main():
    # data_json = requests.post(tg_url + '/getUpdates', data = {'offset': -15}), 
    print("="*60)

if __name__ == '__main__':
    main()

