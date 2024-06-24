from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Column, Start, Url, SwitchTo, Row
from aiogram_dialog.widgets.media import DynamicMedia
from core.dialogs.getters import get_menu_media
from core.states.main_menu import MainMenuStateGroup
from core.utils.texts import _
from settings import settings


main_menu_dialog = Dialog(
    # menu
    Window(
        DynamicMedia(selector='media_content'),
        Format(text='{msg_text}'),
        SwitchTo(Const(text='👍 Хочу принять участие в квесте'), id='go_to_start_info', state=MainMenuStateGroup.start_info),
        SwitchTo(Const(text='❓ Помощь'), id='go_to_help', state=MainMenuStateGroup.help),
        getter=get_menu_media,
        state=MainMenuStateGroup.menu,
    ),

    # start_info
    Window(
        Const(text='Отправляйтесь на поиск первой таблички, изучайте информацию и сканируйте QR 🔎'),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=MainMenuStateGroup.menu),
        state=MainMenuStateGroup.start_info,
    ),

    # help
    Window(
        Const(text='Мы готовы ответить на все ваши вопросы на стойке Города Неравнодушных!'),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=MainMenuStateGroup.menu),
        state=MainMenuStateGroup.help,
    ),
)
