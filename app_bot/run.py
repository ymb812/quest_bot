import asyncio
import logging
import core.middlewares
from aiogram import Bot, Dispatcher, filters
from aiogram_dialog import setup_dialogs, DialogManager, StartMode, ShowMode
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState, OutdatedIntent
from settings import settings
from setup import register
from core.handlers import routers
from core.dialogs import dialogues
from core.states.main_menu import MainMenuStateGroup
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

logger = logging.getLogger(__name__)


async def handle_unknown_intent_or_state(event, dialog_manager: DialogManager):
    logger.error('Restarting dialog: %s', event.exception)
    await dialog_manager.start(
        MainMenuStateGroup.menu, mode=StartMode.RESET_STACK, show_mode=ShowMode.DELETE_AND_SEND,
    )


async def handle_outdated_intent(event, dialog_manager: DialogManager):
    logger.error('Skip error with outdated_intent: %s', event.exception)


bot = Bot(settings.bot_token.get_secret_value(), parse_mode='HTML')

storage = RedisStorage.from_url(
    url=f'redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_name}',
    key_builder=DefaultKeyBuilder(with_destiny=True)
)
dp = Dispatcher(storage=storage)
core.middlewares.i18n.setup(dp)
setup_dialogs(dp)

# handle errors for old dialog
dp.errors.register(
    handle_unknown_intent_or_state,
    filters.ExceptionTypeFilter(UnknownIntent, UnknownState),
)
# skip outdated error
dp.errors.register(
    handle_outdated_intent,
    filters.ExceptionTypeFilter(OutdatedIntent),
)

for _r in routers + dialogues:
    dp.include_router(_r)


async def main():
    async with register():
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
