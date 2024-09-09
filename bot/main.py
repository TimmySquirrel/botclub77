import bot_scripts as bs, time 
from bot_scripts import tg_url
from config import token_vk, channel_id

if __name__ == '__main__':
    while True:
        try:
            AnswerTG = bs.SendMSG2Telegram(tg_url, bs.GetMsgFromVK(token_vk), channel_id)
            time.sleep(5)
            bs.MessageReplies(tg_url, AnswerTG)
        except Exception:
            # logger.warning("Переподключение")
            time.sleep(10)
            pass

    
    



