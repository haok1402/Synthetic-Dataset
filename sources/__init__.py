import logging

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger("synthetic-dataset")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
