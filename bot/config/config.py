#шаблон вывода сообщения в лог можно поднастроить под себя (https://docs.python.org/3/library/logging.html#logrecord-attributes)
log_pattern= u'%(asctime)s #%(levelname)-8s #FUNC:%(funcName)-20s[LINE:%(lineno)-3d]MSG:"%(message)s"' 
#путь к папке куда будет писаться лог
log_path = 'logs'
#делиметр для пути (на Linux в другую сторону? изменить)
delimetr = '/'
#имя файла логаы
log_file_name = 'log.log'
#настройка видимости лога 10 с DEBUG 20 без DEBUG(param for production) 30 WARNING и выше
log_level = 20 
#ожидание перед отправкой продолжения
limit_timeout = 5 
#максимальная длинная сообщения в ТГ с фото
max_len_msg = 1024
# шаг отступа при нахождение максимально допустимой длинны
step_size = 10 
#кол-во топиков для поиска поста (должно быть отрицательным чтоб считать с конца)
get_updates_offset = -50 
# мод парсинга может быть HTML или 
parse_mode = 'HTML'
# версионость
major_ver = 1
minor_ver = 0
micro_ver = 7
version = '{}.{}.{:03d}'.format(major_ver, minor_ver, micro_ver)

url_4_tgbot = "https://api.telegram.org/bot"