import logging
import os
import sys

def setup_logging():
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(level=numeric_level, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
    
    # NOTE: Suppress logging from noisy libraries
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

    # NOTE: Set groq library logging level
    groq_log_level = os.getenv('GROQ_LOG', 'WARNING').upper()
    groq_numeric_level = getattr(logging, groq_log_level, logging.WARNING)
    logging.getLogger('groq').setLevel(groq_numeric_level)

    # NOTE: Set openai library logging level
    openai_log_level = os.getenv('OPENAI_LOG', 'WARNING').upper()
    openai_numeric_level = getattr(logging, openai_log_level, logging.WARNING)
    logging.getLogger('openai').setLevel(openai_numeric_level)