from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from core.dialogs.getters import get_menu_media
from core.dialogs.callbacks import MainMenuCallbackHandler
from core.states.main_menu import MainMenuStateGroup
from core.utils.texts import _

main_menu_dialog = Dialog(
    # menu
    Window(
        DynamicMedia(selector='media_content'),
        Format(text='{msg_text}'),
        Button(Const(
            text='👍 Хочу принять участие в квесте'),
            id='start_first_quest',
            on_click=MainMenuCallbackHandler.start_first_quest
        ),
        SwitchTo(Const(text='❓ Помощь'), id='go_to_help', state=MainMenuStateGroup.help),
        getter=get_menu_media,
        state=MainMenuStateGroup.menu,
    ),

    # help
    Window(
        Const(text='Мы готовы ответить на все ваши вопросы на стойке Города Неравнодушных!'),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=MainMenuStateGroup.menu),
        state=MainMenuStateGroup.help,
    ),
)
