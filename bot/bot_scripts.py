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
    return Result

# Ищем перенос
def GetIndexLastNewLine(text: str):
    a = text.rfind('\n', 0, 800)
    return a if a != -1 else 800

# Получаем пост из ВК
def GetMsgFromVK(token_vk):
    # открываем сессию  с ВК
    print("GetMsgFromVK start ...")
    vk = vk_api.VkApi(token=token_vk)
    longpoll = VkBotLongPoll(vk, group_id=group_id)
    print("Connect to service VK. Session.verify -", longpoll.session.verify.__str__())
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
def SendMSG2Telegram(url, post_param, chat_id):
    print("SendMSG2Telegram start ...")
    if len(post_param['photo']) == 0:
        r = requests.post(url + '/sendMessage', data={"chat_id": chat_id, 
                                                      "text": post_param['text']})
                                                    #   "text": post_param['text'], 
                                                    #   "disable_web_page_preview": True})  
        print(f"SendMSG2Telegram /sendMessage [{r.status_code}]")       
    else:
        text = post_param['text']
        if len(post_param['text']) > 1024:
            a = GetIndexLastNewLine(post_param['text'])
            text = post_param['text'][:a] + f"\n[Все не влезло, продолжение по ссылке {post_param['link']} ©MSGBot]"
            post_param['text'] = ''
            # text = post_param['text'][:a] + '\n[Все не влезло, перенес в комментарии...©MSGBot] '
            # logger.info("Все не влезло, перенес в комментарии...")
            # post_param['text'] = '[На чем мы тут остановились...©MSGBot]\n' + post_param['text'][a:]
        else:
            post_param['text'] = ''
        r = requests.post(url + "/sendPhoto", data={"chat_id": chat_id, 
                                                    "photo": post_param['photo'], 
                                                    "caption": text}) 
        print(f"SendMSG2Telegram /sendPhoto [{r.status_code}]") 
    return post_param if r.status_code == 200 else None  

# Закрепляем пост
def pinChatMessage(url, chat_id, message_id):
    r = requests.post(url + '/pinChatMessage', data = {"chat_id": chat_id, "message_id": message_id})  
    print(f"pinChatMessage /pinChatMessage [{r.status_code}]") 

# комметрируем пост, параметры поста получаем через getUpdates
def MessageReplies(url, post_param):
    print("MessageReplies start ...") 
    if post_param == None : exit()
    r = requests.post(url + '/getUpdates')
    print(f"MessageReplies /getUpdates [{r.status_code}]") 
    if r.status_code == 200:
        Dict = r.json()
        Len_Dict = len(Dict['result'])-1
        Last_Result = Dict['result'][Len_Dict]
        Owner_Channel_ID = Last_Result['message']['chat']['id']
        Reply_ID = Last_Result['message']['message_id'] 
        if post_param['text'] != '':
            # logger.info("post_param['text'] != ''")
            r = requests.post(url + '/sendMessage', data={"chat_id": Owner_Channel_ID, 
                                                          "reply_to_message_id": Reply_ID, 
                                                          "text": post_param['text']}) 
            print(f"MessageReplies /sendMessage [{r.status_code}]") 
            # делаем закреп
            pinChatMessage(url, r.json()['result']['chat']['id'], r.json()['result']['message_id'])
        if post_param['poll'] != '': 
            # logger.info("post_param['poll'] != ''")
            r = requests.post(url + '/sendPoll', data={"chat_id": Owner_Channel_ID, 
                                                       "reply_to_message_id": Reply_ID, 
                                                       "question": post_param['poll'][0], 
                                                       "options": json.dumps(post_param['poll'][1]), 
                                                       "is_anonymous": False})  
            print(f"MessageReplies /sendPoll [{r.status_code}]")

if __name__ == '__main__':
    while True:
        try:
            print("Begin ...")
            AnswerTG = SendMSG2Telegram(tg_url, GetMsgFromVK(token_vk), channel_id)
            time.sleep(5)
            MessageReplies(tg_url, AnswerTG)
            print("End.")
        except Exception:
            # logger.warning("Переподключение")
            print("Something is wrong...")
            time.sleep(10)
            pass