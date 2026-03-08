import logging
import config

def setup_logger():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(config.AGENT_NAME)
