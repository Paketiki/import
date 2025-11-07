from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_NAME: str
    JWT_ALGORITHM: str
    JWT_SECRET_KEY: str

    @property
    def get_db_url(self):
        return f"aiosqlite//{self.DB_NAME}"

    @property
    def auth_data(self):
        return {"algorithm": {self.JWT_ALGORITHM}, "secret_key": {self.JWT_SECRET_KEY}}


settings = Settings()
