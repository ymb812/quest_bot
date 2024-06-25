from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.utils.texts import _
from settings import settings


def mailing_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('MAILING_BUTTON'), callback_data='start_mailing')
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


def answers_kb(quest_id: str | int, answers: dict) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for answer in answers:
        kb.button(text=answers[answer], callback_data=f'answer_{quest_id}_{answer}')
        kb.adjust(1)

    return kb.as_markup(resize_keyboard=True)


def comeback_kb(quest_id: str | int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Вернуться назад', callback_data=f'back_quest_id_{quest_id}')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def followed_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Я подписался!', callback_data='followed')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
