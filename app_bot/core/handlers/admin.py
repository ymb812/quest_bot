import logging
from aiogram import types, Router, F, Bot
from aiogram.utils.i18n import I18n
from core.database.models import User
from settings import settings


logger = logging.getLogger(__name__)
router = Router(name='Admin commands router')


bot = Bot(settings.bot_token.get_secret_value(), parse_mode='HTML')
i18n = I18n(path='locales', default_locale='ru', domain='messages')
i18n.set_current(i18n)


# get file_id for broadcaster
@router.message(F.video | F.video_note | F.photo | F.audio | F.animation | F.sticker | F.document)
async def get_hash(message: types.Message):
    if (await User.get(user_id=message.from_user.id)).status != 'admin':
        return

    if message.video:
        hashsum = message.video.file_id
    elif message.video_note:
        hashsum = message.video_note.file_id
    elif message.photo:
        hashsum = message.photo[-1].file_id
    elif message.audio:
        hashsum = message.audio.file_id
    elif message.animation:
        hashsum = message.animation.file_id
    elif message.sticker:
        hashsum = message.sticker.file_id
    elif message.document:
        hashsum = message.document.file_id
    else:
        return

    await message.answer(f'<code>{hashsum}</code>')
