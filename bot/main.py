import time, codecs 
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





r = requests.post(tg_url + '/getUpdates') 
                                                # 'offset': -10, '
json_file = r.json()
print(GetChatAndMSGID(json_file, -1002162249193, 146))
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
# with open('file/data_update.json') as file:
#     json_file = json.load(file)
# # #     # print(json_file["result"][0])
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

    



