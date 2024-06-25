from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from core.database.models import Quest
from core.handlers.welcome import quest_handler


class MainMenuCallbackHandler:
    @staticmethod
    async def start_first_quest(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        quest = await Quest.get(id=1)
        await quest_handler(message=callback.message, bot=dialog_manager.event.bot, quest=quest)
        await dialog_manager.done()
