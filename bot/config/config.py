log_pattern= u'%(asctime)s #%(levelname)-8s #FUNC:%(funcName)-20s[LINE:%(lineno)-3d]MSG:"%(message)s"'
log_path = 'logs'
log_file_name = 'log.log'
log_level = 20 #настройка видимости лога 10 с DEBUG 20 без DEBUG(param for production)
limit_timeout = 3 #ожидание перед отправкой продолжения
max_len_msg = 1024 #максимальная длинная сообщения в ТГ с фото
get_updates_offset = -50 #кол-во топиков для поиска поста (должно быть отрицательным чтоб считать с конца)
url_4_tgbot = "https://api.telegram.org/bot"