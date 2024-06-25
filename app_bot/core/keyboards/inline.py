from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def answers_kb(quest_id: str | int, answers: dict) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for answer in answers:
        kb.button(text=answer, callback_data=f'answer_{quest_id}_{answer}')
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


def go_to_main_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Главное меню', callback_data=f'go_to_main_menu')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
