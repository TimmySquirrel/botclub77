import time 
from bot_scripts import *
from config import token_vk, channel_id

if __name__ == '__main__':
    while True:
        try:
            AnswerTG = SendMSG2Telegram(tg_url, GetMsgFromVK(token_vk), channel_id)
            time.sleep(5)
            MessageReplies(tg_url, AnswerTG)
        except Exception:
            # logger.warning("Переподключение")
            time.sleep(10)
            pass

    
    



