import list_name

from loguru import logger

if list_name.is_spb_flag():
    logger.add('logs_spb.log', encoding="utf8", rotation='15 MB', compression='zip', level="DEBUG")
    logger.add('logs_spb.log', encoding="utf8", rotation='15 MB', compression='zip', level="INFO")
else:
    logger.add('logs.log', encoding="utf8", rotation='15 MB', compression='zip', level="DEBUG")
    logger.add('logs.log', encoding="utf8", rotation='15 MB', compression='zip', level="INFO")
