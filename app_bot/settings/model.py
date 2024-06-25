from pydantic import BaseModel, SecretStr, fields
from pydantic_settings import SettingsConfigDict


class BotSettings(BaseModel):
    bot_token: SecretStr = fields.Field(max_length=100, alias='TELEGRAM_BOT_TOKEN')
    admin_password: SecretStr = fields.Field(max_length=100, alias='ADMIN_PASSWORD')
    welcome_post_id: int = fields.Field(alias='WELCOME_POST_ID')
    channel_id: int = fields.Field(alias='CHANNEL_ID')


class Dialogues(BaseModel):
    items_per_page_height: int = fields.Field(alias='ITEMS_HEIGHT')
    items_per_page_width: int = fields.Field(alias='ITEMS_WIDTH')


class AppSettings(BaseModel):
    prod_mode: bool = fields.Field(alias='PROD_MODE', default=False)
    excel_file: str = fields.Field(alias='EXCEL_FILE', default='Users stats.xlsx')
    tax_percent: float = fields.Field(alias='TAX_PERCENT', default=5)


class PostgresSettings(BaseModel):
    db_user: str = fields.Field(alias='POSTGRES_USER')
    db_host: str = fields.Field(alias='POSTGRES_HOST')
    db_port: int = fields.Field(alias='POSTGRES_PORT')
    db_pass: SecretStr = fields.Field(alias='POSTGRES_PASSWORD')
    db_name: SecretStr = fields.Field(alias='POSTGRES_DATABASE')


class RedisSettings(BaseModel):
    redis_host: str = fields.Field(alias='REDIS_HOST')
    redis_port: int = fields.Field(alias='REDIS_PORT')
    redis_name: str = fields.Field(alias='REDIS_NAME')


class Settings(
    BotSettings,
    Dialogues,
    AppSettings,
    PostgresSettings,
    RedisSettings
):
    model_config = SettingsConfigDict(extra='ignore')
