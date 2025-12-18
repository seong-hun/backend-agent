import logging

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(fmt=logging.Formatter(fmt="%(asctime)s - %(message)s"))
logger.addHandler(handler)
