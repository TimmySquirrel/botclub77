import vk_api, requests, time, json, logging, os, bot_parser as pe
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config.bot_config import token_telegram, token_vk, group_id, channel_id 
from config.config import *

tg_url = url_4_tgbot + token_telegram
logger = logging.getLogger(__name__)


def isDonat(aJSON:dict)-> bool: 
    logger.debug('Check is donat...')
    return aJSON['donut']['is_donut'] if aJSON.get('donut') else False 

# формируем свой JSON параметров по полученому из VK
def GetValuesJSON(aJSON:dict):
    # инициализируем структуру данных на выходе
    Result = {'text': '', 'photo': [], 'poll': {}, 'link': ''}
    # Получаем текст сообщения + ссылку на пост
    if aJSON['text'] > '':
        Result['text'] = aJSON['text']+'\n\n'
    Result['link'] = f'https://vk.com/wall{aJSON["owner_id"]}_{aJSON["id"]}'
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
                Result['photo'].append(attach['doc']['preview']['photo']['sizes'][-1]['src'])
    return Result

# Ищем перенос
def GetIndexLastNewLine(text: str, max_len: int)-> int:
    a = text.rfind('\n', 0, max_len)
    return a if a != -1 else max_len

def GetIndexMainTextEnd(text: str, max_len: int)-> int:
    a = GetIndexLastNewLine(text, max_len)
    return a if len(pe.ReplaceLink4Photo(text[:a])) <= max_len else GetIndexMainTextEnd(text, max_len - step_size) 

# Получаем пост из ВК
def GetMsgFromVK(token_vk: str):
    # открываем сессию  с ВК
    logger.info('GetMsgFromVK start ...')
    vk = vk_api.VkApi(token=token_vk)
    longpoll = VkBotLongPoll(vk, group_id=group_id)
    logger.info(f'GetMsgFromVK connect to VK service [{longpoll.session.verify.__str__()}]')
    # слушаем отклики сервака
    for event in longpoll.listen():
        if event.type == VkBotEventType.WALL_POST_NEW:
            json_file = event.object
            if (json_file['from_id'] == group_id * -1) and not isDonat(json_file):
                logger.info('GetMsgFromVK finish.')
                return GetValuesJSON(json_file['copy_history'][0]) if json_file.get('copy_history') else GetValuesJSON(json_file)
    

        
# Отправляем в телегу сообщение
def SendMSG2Telegram(url: str, post_param: dict, chat_id: int):
    logger.info('SendMSG2Telegram start ...')
    text = post_param['text'] + post_param['link']
    if len(post_param['photo']) == 0:
        text = pe.ReplaceLink4MSG(text, parse_mode)
        r = requests.post(url + '/sendMessage', data={'chat_id': chat_id,
                                                      'text': text,
                                                      'parse_mode': parse_mode})
        PrintLog(r, 'SendMSG2Telegram', '/sendMessage')
        post_param['text'] = ''
    else:
        Len = len(text) 
        logger.debug(f'Upload msg len {Len}')
        if Len > max_len_msg:
            a = GetIndexMainTextEnd(text, max_len_msg)
            logger.debug(f'Main msg len {a}')
            post_param['text'] = '[Продолжение...]\n' + text[a:]
            text = text[:a]
            Len = len(post_param['text'])
            logger.debug(f'Rep msg len[{Len}]')
        else:
            post_param['text'] = ''
            logger.debug(f'Rep msg empty')
        text = pe.ReplaceLink4Photo(text)
        r = requests.post(url + '/sendPhoto', data={'chat_id': chat_id,
                                                    'photo': post_param['photo'],
                                                    'caption': text})
        PrintLog(r, 'SendMSG2Telegram', '/sendPhoto')
    if r.status_code == 200:
        post_param.update({'owner_chat_id': r.json()['result']['chat']['id'], 'owner_message_id': r.json()['result']['message_id']})
    logger.info('SendMSG2Telegram finish.')
    return post_param if r.status_code == 200 else None


# Закрепляем пост
def pinChatMessage(url:str, chat_id:int, message_id:int):
    r = requests.post(url + '/pinChatMessage', data = {'chat_id': chat_id, 'message_id': message_id})
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
    logger.info('MessageReplies start ...') 
    if post_param != None: 
        ChatParam = GetChatAndMSGID(post_param['owner_chat_id'], post_param['owner_message_id'])
        logger.debug(ChatParam)
        if ChatParam:
            logger.debug(post_param['text'])
            if post_param['text'] != '':  
                text = pe.ReplaceLink4MSG(post_param['text'] , parse_mode)     
                r = requests.post(url + '/sendMessage', data={'chat_id': ChatParam['chat_id'], 
                                                            'reply_to_message_id': ChatParam['message_id'], 
                                                            'parse_mode': parse_mode,
                                                            'text': text 
                                                            })
                PrintLog(r,'MessageReplies', '/sendMessage') 
            else:
                logger.info('Rep msg empty. Dont send')
            logger.debug(post_param['poll'])
            if post_param['poll'] != {}: 
                r = requests.post(url + '/sendPoll', data={'chat_id': ChatParam['chat_id'], 
                                                        'reply_to_message_id': ChatParam['message_id'], 
                                                        'question': post_param['poll'][0], 
                                                        'options': json.dumps(post_param['poll'][1]), 
                                                        'is_anonymous': False})  
                PrintLog(r,'MessageReplies', '/sendPoll') 
            else: logger.info('Poll empty. Dont send')
        else: logger.warning('GetChatAndMSGID dont find main post [CID:{}][MID:{}]'.format(post_param['owner_chat_id'], post_param['owner_message_id']))
    logger.info('MessageReplies finish.') 

#отправка сообщения в лог
def PrintLog(requests, FunName, MetodName: str):
    msg = f'{FunName} {MetodName} [{requests.status_code}]'
    if requests.status_code == 200:
        logger.info(msg)
    else:
        logger.warning(msg + f'[{requests.text}]')

if __name__ == '__main__':
    if not os.path.isdir(log_path):
        try:
            os.mkdir(log_path)
        except: 
            logger.error(f'Dir [{log_path}] not create. Plz try again')
            exit()
    logging.basicConfig(format = log_pattern, level = log_level, filename = log_path + delimetr + log_file_name)
    count_inter = 0
    bad_iter = 0
    logger.info(f'Bot version[{version}] start')
    while True:
        logger.info('='*100)
        count_inter += 1
        try:
            logger.info(f'Start iteration[T:{count_inter}][B:{bad_iter}] ...')
            text = GetMsgFromVK(token_vk)
            if text:
                AnswerTG = SendMSG2Telegram(tg_url, text, channel_id)
                if AnswerTG:
                    time.sleep(limit_timeout)
                    MessageReplies(tg_url, AnswerTG)
            logger.info(f'Finish iteration[T:{count_inter}][B:{bad_iter}].')
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as error:
            logger.warning(error)
            time.sleep(60)
        except Exception as error:
            logger.error(f'Something is wrong...[{type(error)}:{error}]')
            bad_iter += 1
            time.sleep(10)
            pass