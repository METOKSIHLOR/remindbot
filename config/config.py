from dataclasses import dataclass
from environs import Env

@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту

@dataclass
class Postgres:
    user: str
    password: str
    url: str
@dataclass
class Config:
    bot: TgBot
    postgres: Postgres


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        bot=TgBot(token=env("BOT_TOKEN")), postgres=Postgres(user=env("POSTGRES_USER"),
                                                             password=env("POSTGRES_PASSWORD"),
                                                             url=env("POSTGRES_URL")))
