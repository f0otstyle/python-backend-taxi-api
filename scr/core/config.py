from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DB_HOST: str
    DB_PORT: int
    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_redis(self):
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


    model_config = SettingsConfigDict(env_file=".env")


settings = Setting()
