import logging

handler = logging.StreamHandler()
fmt = "%(asctime)s | %(levelname)s | %(message)s"
formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)
logger = logging.getLogger("dataset")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
