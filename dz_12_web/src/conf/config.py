import os

from dotenv import load_dotenv

load_dotenv()

NAME = os.getenv('NAME')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')


class Config:
    DB_URL = f'postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}/{NAME}'


config = Config
 