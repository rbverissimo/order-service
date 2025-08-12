import os
import logging
import sys

class Settings:
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BROKER', 'kafka:9092')

class LoggerConfig:

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'info').lower()
    
    def __init__(self):
        pass

    def setup_logging(self):
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.setLevel(self.__logLevel(self.LOG_LEVEL))

        if root_logger.hasHandlers():
            root_logger.handlers.clear()
        
        root_logger.addHandler(console_handler)
        logging.debug('Logging config setup!')


    def __logLevel(self, level: str):
        switcher = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warn': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }

        log_level = switcher.get(level, logging.INFO)
        return log_level