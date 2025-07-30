import os

class Settings:
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BROKER', 'kafka:9092')