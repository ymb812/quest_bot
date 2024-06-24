import logging
from aiogram import Bot, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram_dialog import DialogManager, StartMode
from core.states.main_menu import MainMenuStateGroup
from core.utils.texts import set_user_commands, set_admin_commands, _
from core.database.models import User


logger = logging.getLogger(__name__)
router = Router(name='Start router')


@router.message(Command(commands=['start']), StateFilter(None))
async def start_handler(message: types.Message, bot: Bot, state: FSMContext, dialog_manager: DialogManager):

    try:
        await dialog_manager.reset_stack()
    except:
        pass

    # add basic info to db
    await User.update_data(
        user_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
        language_code=message.from_user.language_code,
        is_premium=message.from_user.is_premium,
    )

    user = await User.get(user_id=message.from_user.id)
    if user.status == 'admin':
        await set_admin_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=message.from_user.id))
    else:
        await set_user_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=message.from_user.id))

    # # send welcome msg from DB
    # welcome_post = await Post.get(id=settings.welcome_post_id)
    # await message.answer_photo(photo=welcome_post.photo_file_id, caption=welcome_post.text)

    await dialog_manager.start(state=MainMenuStateGroup.menu, mode=StartMode.RESET_STACK)
