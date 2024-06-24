from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.utils.texts import _
from settings import settings


def mailing_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('MAILING_BUTTON'), callback_data='start_mailing')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


# send after reg, cuz we cannot start dialog directly to user
def menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('PROFILE_BUTTON'), callback_data='profile')
    kb.button(text=_('P2P_BUTTON'), callback_data='p2p_market')
    kb.button(text=_('LINK_TO_CHANNEL_BUTTON'), url=settings.help_channel_link)
    kb.button(text=_('LINK_TO_HELP_BUTTON'), url=settings.help_account_link)
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def confirm_kb(user_id: int, request_id: int | None = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('APPROVE_BUTTON'), callback_data=f'request_{request_id}-approve_{user_id}')
    kb.button(text=_('REJECT_BUTTON'), callback_data=f'request_{request_id}-reject_{user_id}')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def confirm_poker_id_changing_kb(user_id: int, poker_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('APPROVE_BUTTON'), callback_data=f'poker_{poker_id}-approve_{user_id}')
    kb.button(text=_('REJECT_BUTTON'), callback_data=f'poker_{poker_id}-reject_{user_id}')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
