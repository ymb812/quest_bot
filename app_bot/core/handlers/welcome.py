import logging
from aiogram import Bot, types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram_dialog import DialogManager, StartMode
from core.states.main_menu import MainMenuStateGroup
from core.utils.texts import set_user_commands, set_admin_commands, _
from core.database.models import User, Quest, UserQuest, Post
from core.keyboards.inline import answers_kb, comeback_kb, followed_kb, go_to_main_kb
from settings import settings


logger = logging.getLogger(__name__)
router = Router(name='Start router')


@router.message(Command(commands=['start']), StateFilter(None))
async def start_handler(message: types.Message, bot: Bot, dialog_manager: DialogManager):
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

    if len(message.text.split(' ')) == 2 and settings.start_deeplink not in message.text:
        deeplink = message.text.split(' ')[-1]
        quest = await Quest.get_or_none(deeplink=deeplink)
        if quest:
            # send quest
            await quest_handler(message=message, bot=bot, quest=quest)
            return

    await dialog_manager.start(state=MainMenuStateGroup.menu, mode=StartMode.RESET_STACK)


async def quest_handler(message: types.Message, bot: Bot, quest: Quest):
    # check if the user completed the previous quest
    if quest.id > 1:
        user_quest_before = await UserQuest.filter(quest_id=quest.id - 1, user_id=message.from_user.id)
        if not user_quest_before:
            await message.answer(
                text='Упс...кажется, ты отсканировал не тот QR-код, пропустив предыдущие таблички. Для нас очень важно, чтобы ты ответил на все вопросы по порядку, поэтому постарайся найти нужную табличку ❤️'
            )
            return

    # send final quest
    if quest.id == 7:
        await message.answer(text=quest.question, reply_markup=followed_kb())

    else:
        # send quest
        await message.answer(text=quest.question, reply_markup=answers_kb(quest_id=quest.id, answers=quest.answers))


# check answer
@router.callback_query(lambda c: 'answer_' in c.data)
async def quest_answer_handler(callback: types.CallbackQuery, bot: Bot):
    await callback.message.delete()

    data = callback.data.split('_')
    quest_id = int(data[1])
    answer = data[-1]

    quest = await Quest.get_or_none(id=quest_id, correct_answer=answer)
    if not quest:
        await callback.message.answer(
            text='Упс, ошибка. Прочитайте еще раз информацию с таблички, нажмите на кнопку “Вернуться назад” и попробуйте ещё раз, всё обязательно получится!',
            reply_markup=comeback_kb(quest_id=quest_id)
        )

    else:
        welcome_post = await Post.get(id=settings.welcome_post_id)
        await callback.message.answer_photo(
            caption=quest.final_phrase,
            photo=welcome_post.photo_file_id,
            reply_markup=go_to_main_kb()
        )

        # add log
        await UserQuest.create(
            user_id=callback.from_user.id,
            quest_id=quest_id,
        )


# back button
@router.callback_query(lambda c: 'back_quest_id_' in c.data)
async def quest_answer_handler(callback: types.CallbackQuery, bot: Bot):
    await callback.message.delete()

    quest_id = callback.data.split('_')[-1]
    quest = await Quest.get_or_none(id=quest_id)
    # send quest
    await callback.message.answer(
        text=quest.question, reply_markup=answers_kb(quest_id=quest.id, answers=quest.answers)
    )


# followed
@router.callback_query(F.data == 'followed')
async def followed_handler(callback: types.CallbackQuery, bot: Bot):
    quest = await Quest.get_or_none(id=7)

    # check channel for user
    chat_member = await bot.get_chat_member(user_id=callback.from_user.id, chat_id=settings.channel_id)
    if chat_member.status not in ['creator', 'administrator', 'member', 'restricted']:
        logger.info(f'user_id={callback.from_user.id} is not in the chat')

        await callback.message.delete()
        await callback.message.answer(text=quest.question, reply_markup=followed_kb())
    else:
        await callback.message.answer(text=quest.final_phrase, reply_markup=go_to_main_kb())


@router.callback_query(F.data == 'go_to_main_menu')
async def followed_handler(callback: types.CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(state=MainMenuStateGroup.menu, mode=StartMode.RESET_STACK)


@router.message(Command(commands=['help']))
async def help_handler(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=MainMenuStateGroup.help, mode=StartMode.RESET_STACK)
