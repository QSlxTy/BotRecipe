import logging
from dataclasses import dataclass
from os import getenv

from sqlalchemy.engine import URL

from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:

    name: str | None = getenv('PYMYSQL_DATABASE')
    user: str | None = getenv('PYMYSQL_USER')
    passwd: str | None = getenv('PYMYSQL_PASSWORD', None)
    port: int = int(getenv('PYMYSQL_PORT', 3306))
    host: str = getenv('PYMYSQL_HOST', 'test')

    driver: str = 'aiomysql'
    database_system: str = 'mysql'

    def build_connection_str(self) -> str:
        return URL.create(
            drivername=f'{self.database_system}+{self.driver}',
            username=self.user,
            database=self.name,
            password=self.passwd,
            port=self.port,
            host=self.host,
        ).render_as_string(hide_password=False)

@dataclass
class BotConfig:
    token: str = getenv('BOT_TOKEN')


@dataclass
class Configuration:
    debug = bool(getenv('DEBUG'))
    logging_level = int(getenv('LOGGING_LEVEL', logging.INFO))

    db = DatabaseConfig()
    bot = BotConfig()


conf = Configuration()
