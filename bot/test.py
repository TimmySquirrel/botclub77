import bot


# with open('file/data_repost.json') as file:
#     json_file = json.load(file)
# if json_file.get('copy_history') and json_file['text'] == '':
#     print(json_file['copy_history'][0])
#     print(GetValuesJSON(json_file['copy_history'][0]))


# def GetMsgFromVK(token_vk):
#     vk = vk_api.VkApi(token=token_vk)
#     longpoll = VkBotLongPoll(vk, group_id=group_id)
#     for event in longpoll.listen():
#         if event.type == VkBotEventType.WALL_POST_NEW: 
#             with open('file/data_repost.json', 'w') as file:
#                 json.dump(event.object, file, indent=4)
#             return GetValuesJSON(event.object)

# print(json.dumps(GetMsgFromVK(token_vk), indent=4))


# def send_telegram(text: str):
#     url = "https://api.telegram.org/bot"
#     url += token_telegram
#     method = url + "/sendMessage"
#     r = requests.post(method, data={"chat_id": channel_id, "text": text, "disable_web_page_preview": True})
#     if r.status_code != 200:
#         # logger.warning("Ошибка отправки в телеграм; Код ответа " + str(r.status_code))
#         raise Exception("post_text error")
#     else:
#         # logger.info("Успешно отправлено в телеграм")

# while True:
#     try:
#         vk = vk_api.VkApi(token=token_vk)
#         longpoll = VkBotLongPoll(vk, group_id=group_id)
#         # logger.info("Подключение к VK. Session.verify - " + longpoll.session.verify.__str__())

#         for event in longpoll.listen():
#              if event.type == VkBotEventType.WALL_POST_NEW:
#                  if event.object.from_id == group_id * -1:
#                     #  logger.info("Новая запись на стене от Сообщества")
#                      msg = event.object.text + "\n\nhttps://vk.com/wall-" + str(group_id) + "_" + str(event.object.id)
#                      send_telegram(msg)
#                  else:
#                     #  logger.info("Новая запись на стене от Пользователя - Skip")
#     except Exception:
#         # logger.warning("Переподключение")
#         time.sleep(10)
#         pass