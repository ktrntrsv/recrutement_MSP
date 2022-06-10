from loguru import logger

logger.add('debug.log', encoding="utf8", rotation='10 MB', compression='zip', level="DEBUG")
