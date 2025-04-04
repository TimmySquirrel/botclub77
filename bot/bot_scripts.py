import vk_api, requests, time, json, logging, os
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from bot_config import token_telegram, token_vk, group_id, channel_id 
from config.config import *

# version 1.0.001

tg_url = url_4_tgbot + token_telegram
logger = logging.getLogger(__name__)

# формируем свой JSON параметров по полученому из VK
def GetValuesJSON(aJSON:dict):
    # инициализируем структуру данных на выходе
    Result = {}
    Result['text'] = ''
    Result['photo'] = [] 
    Result['poll'] = {}
    Result['link'] = ''
    # Получаем текст сообщения + ссылку на пост
    if aJSON['text'] > '':
        Result['text'] = aJSON['text']+'\n\n'
    Result['link'] = f"https://vk.com/wall{aJSON['owner_id']}_{aJSON['id']}"
    # Вытаскиваем содержимое прикрепленных элементов
    attachments = [attach for attach in aJSON['attachments']]
    if len(attachments) > 0 :
        for attach in attachments:
            if attach['type'] == 'poll':
                Result['poll'] = (attach['poll']['question'],[ans['text'] for ans in attach['poll']['answers']])
                if attach['poll'].get('photo'):
                    Result['photo'].append(attach['poll']['photo']['images'][0]['url'])
            elif attach['type'] == 'photo':               
                Result['photo'].append(attach['photo']['orig_photo']['url'])
            elif attach['type'] == 'doc':               
                Result['photo'].append(attach['doc']["preview"]['photo']['sizes'][-1]['src'])
    return Result

# Ищем перенос
def GetIndexLastNewLine(text: str):
    a = text.rfind('\n', 0, max_len_msg)
    return a if a != -1 else max_len_msg

# Получаем пост из ВК
def GetMsgFromVK(token_vk: str):
    # открываем сессию  с ВК
    logger.info("GetMsgFromVK start ...")
    vk = vk_api.VkApi(token=token_vk)
    longpoll = VkBotLongPoll(vk, group_id=group_id)
    logger.info(f"GetMsgFromVK connect to VK service [{longpoll.session.verify.__str__()}]")
    # слушаем отклики сервака
    for event in longpoll.listen():
        if event.type == VkBotEventType.WALL_POST_NEW:
            json_file = event.object
            if json_file['from_id'] == group_id * -1:
                logger.info("GetMsgFromVK finish.")
                return GetValuesJSON(json_file['copy_history'][0]) if json_file.get('copy_history') else GetValuesJSON(json_file)
    

        
# Отправляем в телегу сообщение
def SendMSG2Telegram(url: str, post_param: dict, chat_id: int):
    logger.info("SendMSG2Telegram start ...")
    if len(post_param['photo']) == 0:
        r = requests.post(url + '/sendMessage', data={"chat_id": chat_id,
                                                      "text": post_param['text'] + post_param['link'],
                                                      "disable_web_page_preview": True})
                                                    #   "text": post_param['text'],
                                                    #   "disable_web_page_preview": True})
        PrintLog(r, 'SendMSG2Telegram', '/sendMessage')
    else:
        text = post_param['text'] + post_param['link']
        Len = len(text)
        logger.debug(f'Upload msg len {Len}')
        if Len > max_len_msg:
            a = GetIndexLastNewLine(post_param['text'])
            logger.debug(f'Main msg len {a}')
            text = post_param['text'][:a] 
            post_param['text'] = '[Продолжение...]\n' + post_param['text'][a:]
            Len = len(post_param['text'])
            logger.debug(f'Rep msg len[{Len}]')
        else:
            post_param['text'] = ''
            logger.debug(f'Rep msg empty')
        r = requests.post(url + "/sendPhoto", data={"chat_id": chat_id,
                                                    "photo": post_param['photo'],
                                                    "caption": text})
        PrintLog(r, 'SendMSG2Telegram', '/sendPhoto')
    if r.status_code == 200:
        post_param.update({'owner_chat_id': r.json()['result']['chat']['id'], 'owner_message_id': r.json()['result']['message_id']})
    logger.info("SendMSG2Telegram finish.")
    return post_param if r.status_code == 200 else None


# Закрепляем пост
def pinChatMessage(url:str, chat_id:int, message_id:int):
    r = requests.post(url + '/pinChatMessage', data = {"chat_id": chat_id, "message_id": message_id})
    PrintLog(r, 'pinChatMessage', '/pinChatMessage')  

# поиск последнего сообщения
def GetChatAndMSGID(from_chat_id:int, from_msg_id:int):
    data_json = requests.post(tg_url + '/getUpdates', data = {'offset': get_updates_offset})
    PrintLog(data_json, 'GetChatAndMSGID', '/getUpdates')   
    if data_json.status_code == 200:
        logger.info(f'Count msg from group {len(data_json.json())}')
        for result in data_json.json()['result']:
            if (result.get('message')  
                and result['message'].get('is_automatic_forward') 
                and result['message']['forward_from_chat']['id'] == from_chat_id
                and result['message']['forward_from_message_id'] == from_msg_id):
                return {'update_id': result['update_id'], 'message_id': result['message']['message_id'], 'chat_id': result['message']['chat']['id']}
    elif data_json.status_code == 409:
        data_json = requests.post(tg_url + '/deleteWebhook')
        PrintLog(data_json, 'GetChatAndMSGID', '/deleteWebhook') 

# комметрируем пост, параметры поста получаем через getUpdates
def MessageReplies(url:str, post_param:dict):
    logger.info("MessageReplies start ...") 
    if post_param != None: 
        ChatParam = GetChatAndMSGID(post_param['owner_chat_id'], post_param['owner_message_id'])
        logger.debug(ChatParam)
        if ChatParam:
            logger.debug(post_param['text'])
            if post_param['text'] != '':                
                r = requests.post(url + '/sendMessage', data={"chat_id": ChatParam['chat_id'], 
                                                            "reply_to_message_id": ChatParam['message_id'], 
                                                            "text": post_param['text']}) 
                PrintLog(r,"MessageReplies", "/sendMessage") 
            else:
                logger.info('Rep msg empty. Dont send')
            logger.debug(post_param['poll'])
            if post_param['poll'] != {}: 
                r = requests.post(url + '/sendPoll', data={"chat_id": ChatParam['chat_id'], 
                                                        "reply_to_message_id": ChatParam['message_id'], 
                                                        "question": post_param['poll'][0], 
                                                        "options": json.dumps(post_param['poll'][1]), 
                                                        "is_anonymous": False})  
                PrintLog(r,"MessageReplies", "/sendPoll") 
            else:
                logger.info('Poll empty. Dont send')
    logger.info("MessageReplies finish.") 

#отправка сообщения в лог
def PrintLog(requests, FunName, MetodName: str):
    msg = f"{FunName} {MetodName} [{requests.status_code}]"
    if requests.status_code == 200:
        logger.info(msg)
    else:
        logger.warning(msg + f"[{requests.text}]")

if __name__ == '__main__':
    if not os.path.isdir(log_path):
        try:
            os.mkdir(log_path)
        except: 
            logger.error(f'Dir [{log_path}] not create. Plz try again')
            exit()
    logging.basicConfig(format = log_pattern, level = log_level, filename = log_path + '/' + log_file_name)
    count_inter = 0
    bad_iter = 0
    while True:
        count_inter += 1
        try:
            logger.info(f"Start iteration[T:{count_inter}][B:{bad_iter}] ...")
            text = GetMsgFromVK(token_vk)
            if text:
                AnswerTG = SendMSG2Telegram(tg_url, text, channel_id)
                if AnswerTG:
                    time.sleep(limit_timeout)
                    MessageReplies(tg_url, AnswerTG)
            logger.info(f"Finish iteration[[T:{count_inter}][B:{bad_iter}].")
        except Exception as error:
            logger.warning(f"Something is wrong...[{type(error)}:{error}]")
            bad_iter += 1
            time.sleep(10)
            pass
        logger.info("="*60)