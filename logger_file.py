from loguru import logger

import config

if config.spb_flag:
    logger.add('logs_spb.log', encoding="utf8", rotation='15 MB', compression='zip', level="DEBUG")
    logger.add('logs_spb.log', encoding="utf8", rotation='15 MB', compression='zip', level="INFO")
else:
    logger.add('logs.log', encoding="utf8", rotation='15 MB', compression='zip', level="DEBUG")
    logger.add('logs.log', encoding="utf8", rotation='15 MB', compression='zip', level="INFO")