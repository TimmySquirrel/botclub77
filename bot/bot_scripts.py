import vk_api, requests, time, json
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from bot_config import token_telegram, token_vk, group_id, channel_id 



tg_url = "https://api.telegram.org/bot" + token_telegram


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
    a = text.rfind('\n', 0, 800)
    return a if a != -1 else 800

# Получаем пост из ВК
def GetMsgFromVK(token_vk: str):
    # открываем сессию  с ВК
    print("GetMsgFromVK start ...")
    vk = vk_api.VkApi(token=token_vk)
    longpoll = VkBotLongPoll(vk, group_id=group_id)
    print(f"GetMsgFromVK connect to VK service [{longpoll.session.verify.__str__()}]")
    # logger.info("Подключение к VK. Session.verify - " + longpoll.session.verify.__str__())
    # слушаем отклики сервака
    for event in longpoll.listen():
        if event.type == VkBotEventType.WALL_POST_NEW:
            json_file = event.object
            if json_file['from_id'] == group_id * -1:
                # logger.info("Новая запись на стене от Сообщества")
                print("GetMsgFromVK get a new post from API ...")
                return GetValuesJSON(json_file['copy_history'][0]) if json_file.get('copy_history') else GetValuesJSON(json_file)

        
# Отправляем в телегу сообщение
def SendMSG2Telegram(url: str, post_param: dict, chat_id: int):
    print("SendMSG2Telegram start ...")
    if len(post_param['photo']) == 0:
        r = requests.post(url + '/sendMessage', data={"chat_id": chat_id,
                                                      "text": post_param['text'] + post_param['link']})
                                                    #   "text": post_param['text'],
                                                    #   "disable_web_page_preview": True})
        PrintLog(r, 'SendMSG2Telegram', '/sendMessage')
    else:
        text = post_param['text'] + post_param['link']
        if len(post_param['text']) > 1024:
            a = GetIndexLastNewLine(post_param['text'])
            # text = post_param['text'][:a] + f"\n[Все не влезло, продолжение по ссылке {post_param['link']} ©MSGBot]"
            # post_param['text'] = ''
            # logger.info("Все не влезло, перенес в комментарии...")
            text = post_param['text'][:a] + '\n[Все не влезло, перенес в комментарии...] '
            post_param['text'] = '[На чем мы тут остановились...]\n' + post_param['text'][a:] + post_param['link']
        else:
            post_param['text'] = ''
        print(post_param['photo'])
        r = requests.post(url + "/sendPhoto", data={"chat_id": chat_id,
                                                    "photo": post_param['photo'],
                                                    "caption": text})
        PrintLog(r, 'SendMSG2Telegram', '/sendPhoto')
        if r.status_code == 200:
            post_param.update({'owner_chat_id': r.json()['result']['chat']['id'], 'owner_message_id': r.json()['result']['message_id']})
    return post_param if r.status_code == 200 else None


# Закрепляем пост
def pinChatMessage(url:str, chat_id:int, message_id:int):
    r = requests.post(url + '/pinChatMessage', data = {"chat_id": chat_id, "message_id": message_id})
    PrintLog(r, 'pinChatMessage', '/pinChatMessage')  

# поиск последнего сообщения
def GetChatAndMSGID(from_chat_id:int, from_msg_id:int):
    data_json = requests.post(tg_url + '/getUpdates', data = {'offset': -15})
    PrintLog(data_json, 'GetChatAndMSGID', '/getUpdates')  
    if data_json.status_code == 200:
        for result in data_json.json()['result']:
            if (result.get('message')  
                and result['message'].get('is_automatic_forward') 
                and result['message']['forward_from_chat']['id'] == from_chat_id
                and result['message']['forward_from_message_id'] == from_msg_id):
                return {'update_id': result['update_id'], 'message_id': result['message']['message_id'], 'chat_id': result['message']['chat']['id']}

# комметрируем пост, параметры поста получаем через getUpdates
def MessageReplies(url:str, post_param:dict):
    print("MessageReplies start ...") 
    if post_param != None: 
        ChatParam = GetChatAndMSGID(post_param['owner_chat_id'], post_param['owner_message_id'])
        if ChatParam:
            if post_param['text'] != '':
                # logger.info("post_param['text'] != ''")
                r = requests.post(url + '/sendMessage', data={"chat_id": ChatParam['chat_id'], 
                                                            "reply_to_message_id": ChatParam['message_id'], 
                                                            "text": post_param['text']}) 
                PrintLog(r,"MessageReplies", "/sendMessage") 
                # if r.status_code == 200:
                #     # делаем закреп
                #     pinChatMessage(url, r.json()['result']['chat']['id'], r.json()['result']['message_id'])
            if post_param['poll'] != '': 
                # logger.info("post_param['poll'] != ''")
                r = requests.post(url + '/sendPoll', data={"chat_id": ChatParam['chat_id'], 
                                                        "reply_to_message_id": ChatParam['message_id'], 
                                                        "question": post_param['poll'][0], 
                                                        "options": json.dumps(post_param['poll'][1]), 
                                                        "is_anonymous": False})  
                PrintLog(r,"MessageReplies", "/sendPoll") 

def PrintLog(requests, FunName: str, MetodName: str):
   print(f"{FunName} {MetodName} [{requests.status_code}]" + ('' if requests.status_code == 200 else f"[{requests.text}]")) 

if __name__ == '__main__':
    while True:
        try:
            print("Begin ...")
            text = GetMsgFromVK(token_vk)
            AnswerTG = SendMSG2Telegram(tg_url, text, channel_id)
            time.sleep(5)
            MessageReplies(tg_url, AnswerTG)
            print("End.")
        except Exception:
            # logger.warning("Переподключение")
            print(f"Something is wrong...")
            time.sleep(10)
            pass