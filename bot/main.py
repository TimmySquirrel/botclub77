import time, codecs, re
from bot_scripts import *
from bot_config import token_vk, channel_id

# if __name__ == '__main__':
#     while True:
#         try:
#             AnswerTG = SendMSG2Telegram(tg_url, GetMsgFromVK(token_vk), channel_id)
#             time.sleep(5)
#             MessageReplies(tg_url, AnswerTG)
#         except Exception:
#             # logger.warning("Переподключение")
#             time.sleep(10)
#             pass

file_name_string = 'file/{}.json'

#   Сохранить текст в файл с  ВК 
def SaveMsgFromVK(token_vk, file_name):
    vk = vk_api.VkApi(token=token_vk)
    longpoll = VkBotLongPoll(vk, group_id=group_id)
    for event in longpoll.listen():
        if event.type == VkBotEventType.WALL_POST_NEW: 
            # with open('file/' +file_name + '.json', 'w') as file:
            with open(file_name_string.format(file_name), 'w') as file:
                json.dump(event.object, file, indent=4)
            # return GetValuesJSON(event.object)

# SaveMsgFromVK(token_vk,'msg_with_link')


#  чтение JSON
def ReadJSON(file_name) -> str:
    with open(file_name_string.format(file_name)) as file:
        json_file = json.load(file)
        message = json_file['copy_history'][0]['text']
        return message

def ParsString(aPattern, aString: str):
    ar_text = re.findall(aPattern, aString) 
    return ar_text if len(ar_text) != 0 else None 

def ReplceLinkByTG(aString:str): 
    _PatterMain = r"\[#alias\|.*\]"
    _PatterBefor = r"\[#alias\|(.*)\|(.*)\]"
    _PatterMarkTG = '[{}]({})'
    _PatterHTMLTG = '<a href="{}">{}</a>'
    while True:
        _Text = re.search(_PatterMain, aString)
        if _Text:
            _LinkPart = re.findall(_PatterBefor, _Text[0])
            if _LinkPart:
                _TextAfter = _PatterMarkTG.format(_LinkPart[0][0], _LinkPart[0][1])
                aString = aString.replace(_Text[0], _TextAfter)
        else: break
    return aString       
    



# _LinkString = '[{}]({})'
_JSON_Text = ReadJSON('msg_with_link')
_Text4TG = {'text':'', 'photo':[], 'poll': {}, 'link':''}
print(_JSON_Text)
_JSON_Text = _JSON_Text.replace('_', '\_')
_Text4TG['text'] = ReplceLinkByTG(_JSON_Text)
SendMSG2Telegram(tg_url, _Text4TG, channel_id)

# _Pattern1 = r"\[(.*)\]"
# _Pattern2 = r"\[#alias\|(.*)\|(.*)\]"
# _Pattern3 = "\[#alias\|{}\|{}\]"
# text = ParsString(_Pattern2, _JSON_Text)

# if text:
#     _List = [_LinkString.format(string[0],string[1]) for string in text] 
#     print(_List)



# r = requests.post(tg_url + '/getUpdates') 
#                                                 # 'offset': -10, '
# json_file = r.json()
# print(GetChatAndMSGID(json_file, -1002162249193, 146))
# print(json.dumps(json_file['result'][0],  indent=4))
# for i,result in enumerate(json_file['result']):
#     if result.get('message') and result['message'].get('is_automatic_forward') and result['message']['forward_from_message_id'] == 146:
#         # print(result)
#         print(i, result['message']['message_id'], result['message']['chat']['id'])
    # if result.get('message') and result['message'].get('sender_chat'):
    #     print(i, result['message'])
        # with open('file/data_update_botresult.json', 'w') as file:
        #     json.dump(result, file, indent=4)
    # if result.get('message') and result['message'].get('sender_chat'):
    #     print(i, result['message'])

# # # with open('file/data_update.json', 'w') as file:
# # #     file.read(r.text)

# with open('file/data_update.json', 'w') as file:
#     json.dump(json.loads(r.text), file, indent=4)
# print(json.dump(json.loads(r.text), ensure_ascii = False,  indent=4))
# print(json.dumps(r.text,  indent=4))

# 
#     # json.dump(r.text, file, indent=4)
# with open('file/data_repost_new1.json') as file:
#     json_file = json.load(file)

#     print(json_file['copy_history'][0]['attachments'][0]['doc']["preview"]['photo']['sizes'][-1]['src'])
# #     # print(json_file["result"][0])
#     for result in json_file["result"]:
        
#         if result.get('message')  and  result['message']['chat']['id'] == -1002430633954: 
#             # and result['message'].get('sender_chat')
#             print(result['message'],'\n')
        # print(json.dumps(result,  indent=4)+'\n')
        # if result.get('channel_post'):
        #     print(result['channel_post'])
        # if result.get('message') and result['message']['from']['is_bot']:
        #     # print(result['message']['chat']['id'], result['message']['message_id'])
        #    print(result['message'])
        
# print(codecs.decode(r.text,'unicode_escape'))
# pinChatMessage(tg_url, -1001195655967)

    



