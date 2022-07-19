from loguru import logger

logger.add('logs.log', encoding="utf8", rotation='15 MB', compression='zip', level="DEBUG")
logger.add('logs.log', encoding="utf8", rotation='15 MB', compression='zip', level="INFO")
