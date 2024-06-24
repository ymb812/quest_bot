import string
import random
import datetime
import pytz
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from core.states.main_menu import MainMenuStateGroup
from core.states.registration import RegistrationStateGroup
from core.states.profile import ProfileStateGroup
from core.states.market import MarketStateGroup
from core.states.rakeback import RakebackStateGroup
from core.states.cards import CardsStateGroup
from core.database.models import Club, User, PaymentRequest, PaymentMethod
from core.keyboards.inline import confirm_kb, confirm_poker_id_changing_kb
from core.utils.texts import _
from settings import settings


def generate_random_string(length: int = 8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def get_username_or_link(user: User):
    if user.username:
        user_username = f'@{user.username}'
    else:
        user_username = f'<a href="tg://user?id={user.user_id}">ссылка</a>'

    return user_username


async def get_datetime() -> str:
    timezone = pytz.timezone('Europe/Moscow')
    date_format = '%d.%m.%Y %H:%M:%S'
    return f'{datetime.datetime.now(timezone).strftime(date_format)}'


class RegistrationCallbackHandler:
    @staticmethod
    async def entered_country(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        dialog_manager.dialog_data['country'] = callback.data
        await dialog_manager.switch_to(state=RegistrationStateGroup.has_poker_id)


    @staticmethod
    async def entered_poker_id(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value,
    ):
        # correct checker
        poker_id = value

        # poker_id unique checker
        user = await User.filter(poker_id=poker_id).first()
        if user:
            await message.answer(text='Пользователь с таким ID уже существует - повторите ввод')
            dialog_manager.dialog_data['poker_id_error'] = True
            return

        dialog_manager.dialog_data['poker_id_error'] = False
        dialog_manager.dialog_data['poker_id'] = value

        # handle 'change_poker_id' from Profile
        if dialog_manager.start_data and dialog_manager.start_data.get('change_poker_id'):
            # save poker_id to db
            await User.filter(user_id=message.from_user.id).update(poker_id=poker_id)

            await message.answer(text=_('POKER_ID_HAS_BEEN_CHANGED', poker_id=poker_id))
            await dialog_manager.start(state=ProfileStateGroup.menu)

        else:
            await dialog_manager.switch_to(state=RegistrationStateGroup.club_input)


    @staticmethod
    async def entered_club(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str
    ):
        club = await Club.get(id=item_id)
        dialog_manager.dialog_data['club_id'] = club.id
        dialog_manager.dialog_data['club_name'] = club.name
        await dialog_manager.switch_to(state=RegistrationStateGroup.request_input)


    @staticmethod
    async def registration_is_done(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        club_id = dialog_manager.dialog_data['club_id']

        # handle 'change_club' from Profile
        if dialog_manager.start_data and dialog_manager.start_data.get('change_club'):
            # save club to db
            await User.filter(user_id=callback.from_user.id).update(club_id=club_id)

            await callback.message.answer(text=_('CLUB_ID_HAS_BEEN_CHANGED', club_id=club_id))
            await dialog_manager.start(state=ProfileStateGroup.menu)

        else:
            user = await User.get(user_id=callback.from_user.id)
            user.country = dialog_manager.dialog_data['country']
            user.poker_id = dialog_manager.dialog_data['poker_id']
            user.club_id = dialog_manager.dialog_data['club_id']
            await user.save()

            await dialog_manager.event.bot.send_message(
                chat_id=settings.admin_chat_id,
                text=_(
                    text='REGISTRATION_DATA_FOR_ADMINS',
                    msg_type='register',
                    user_id=user.user_id,
                    status_type='new',
                    status_msg='🟡 Новый пользователь',
                    username=get_username_or_link(user=user),
                    poker_id=user.poker_id,
                    club_name=dialog_manager.dialog_data['club_name'],
                    club_id=dialog_manager.dialog_data['club_id'],
                    country=user.country,
                    approve_or_reject_msg='',  # for edit
                    admin_username='',  # for edit
                    datetime_msg=await get_datetime(),
                ),
                reply_markup=confirm_kb(user_id=user.user_id)
            )

            await dialog_manager.switch_to(RegistrationStateGroup.registration_is_done)


class ProfileCallbackHandler:
    @staticmethod
    async def entered_poker_id(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value,
    ):
        poker_id = value

        # poker_id unique checker
        user = await User.filter(poker_id=poker_id).first()
        if user:
            await message.answer(text='Пользователь с таким ID уже существует - повторите ввод')
            dialog_manager.dialog_data['poker_id_error'] = True
            return

        user: User = await User.get(user_id=message.from_user.id).select_related('club')
        dialog_manager.dialog_data['poker_id_error'] = False
        dialog_manager.dialog_data['poker_id'] = poker_id

        # send request to admins
        await dialog_manager.event.bot.send_message(
            chat_id=settings.admin_chat_id,
            text=_(
                text='CHANGING_DATA_FOR_ADMINS',
                msg_type='changing',
                user_id=user.user_id,
                status_type='new',
                status_msg='🟡 Изменение ID',
                username=get_username_or_link(user=user),
                old_poker_id=user.poker_id,
                new_poker_id=poker_id,
                club_name=user.club.name,
                club_id=user.club.id,
                country=user.country,
                approve_or_reject_msg='',  # for edit
                admin_username='',  # for edit
                datetime_msg=await get_datetime(),
            ),
            reply_markup=confirm_poker_id_changing_kb(user_id=user.user_id, poker_id=poker_id)
        )

        await message.answer(text='🟡 Заявка на смену ID отправлена на модерацию')
        await dialog_manager.switch_to(state=ProfileStateGroup.menu)


    @staticmethod
    async def start_club_changing(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        await dialog_manager.start(state=RegistrationStateGroup.club_input, data={'change_club': True})


    @staticmethod
    async def entered_country(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        await User.filter(user_id=callback.from_user.id).update(country=callback.data)
        await dialog_manager.switch_to(state=ProfileStateGroup.menu)


class MarketCallbackHandler:
    @staticmethod
    async def buy_or_sell_chips(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        if widget.widget_id == 'buy_chips':
            dialog_manager.dialog_data['action'] = 'buy'
        elif widget.widget_id == 'sell_chips':
            dialog_manager.dialog_data['action'] = 'sell'

        await dialog_manager.switch_to(state=MarketStateGroup.input_amount)


    @staticmethod
    async def entered_chips_amount(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: int,
    ):
        if value > 0:
            dialog_manager.dialog_data['amount'] = value

            # going to pick bank to buy or get card for sale
            if dialog_manager.dialog_data['action'] == 'buy':
                await dialog_manager.switch_to(state=MarketStateGroup.pick_payment)
            elif dialog_manager.dialog_data['action'] == 'sell':
                await dialog_manager.switch_to(state=MarketStateGroup.pick_crypto_or_card_for_sale)


    @staticmethod
    async def pick_bank(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str,
    ):
        dialog_manager.dialog_data['payment_method_id'] = item_id
        payment_method = await PaymentMethod.get(id=item_id)

        if payment_method.is_crypto:
            dialog_manager.dialog_data['is_crypto'] = True
        else:
            dialog_manager.dialog_data['is_crypto'] = False

        await dialog_manager.switch_to(state=MarketStateGroup.input_payment_data)


    # pick crypto or card sale
    @staticmethod
    async def pick_crypto_or_card_for_sale(
            callback: CallbackQuery,
            widget: Button,
            dialog_manager: DialogManager,
    ):
        if callback.data == 'is_crypto_for_sale':
            dialog_manager.dialog_data['is_crypto_for_sale'] = True
            await dialog_manager.switch_to(state=MarketStateGroup.input_payment_data)
        else:
            dialog_manager.dialog_data['is_crypto_for_sale'] = False
            await dialog_manager.switch_to(state=MarketStateGroup.input_card_for_sale)


    # handle card for sale
    @staticmethod
    async def entered_card_for_sale(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: str,
    ):
        dialog_manager.dialog_data['card_for_sale'] = value
        await dialog_manager.switch_to(state=MarketStateGroup.input_payment_data)


    # handle all 3 variants: 'buy bank', 'buy crypto', 'sell'
    @staticmethod
    async def entered_payment_data(
            message: Message,
            widget: MessageInput,
            dialog_manager: DialogManager,
    ):
        payment_method_id, media_file_id = None, None
        if dialog_manager.dialog_data['action'] == 'buy':
            payment_method_id = dialog_manager.dialog_data['payment_method_id']

            # handle photo for buy with card
            if not message.photo:
                return
            data = message.caption
            media_file_id = message.photo[-1].file_id
            dialog_manager.dialog_data['media_file_id'] = media_file_id

        else:
            if dialog_manager.dialog_data['is_crypto_for_sale']:
                data = message.text
            else:
                data = f'{dialog_manager.dialog_data["card_for_sale"]} {message.text}'

        request = await PaymentRequest.create(
            id=generate_random_string(),
            data=data,
            media_file_id=media_file_id,
            action=dialog_manager.dialog_data['action'],
            object=PaymentRequest.RequestObject.chips,
            amount=dialog_manager.dialog_data['amount'],
            usd_price=dialog_manager.dialog_data['amount'],
            user_id=message.from_user.id,
            payment_method_id=payment_method_id,
        )

        dialog_manager.dialog_data['request_id'] = request.id
        await dialog_manager.switch_to(state=MarketStateGroup.request_data)


    @staticmethod
    async def cancel_request(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        await PaymentRequest.filter(id=dialog_manager.dialog_data['request_id']).delete()
        await dialog_manager.switch_to(state=MarketStateGroup.menu)


    @staticmethod
    async def send_request_to_admins(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        if dialog_manager.dialog_data['action'] == 'buy':
            sell_or_buy_text = 'Перевод от:'
        else:
            sell_or_buy_text = 'Заявка от:'

        user = await User.get(user_id=callback.from_user.id)
        club = await user.club

        if dialog_manager.dialog_data.get('media_file_id'):
            await dialog_manager.event.bot.send_photo(
                chat_id=settings.admin_chat_id,
                photo=dialog_manager.dialog_data['media_file_id'],
                caption=_(
                    text='REQUEST_DATA_FOR_ADMINS',
                    msg_type=dialog_manager.dialog_data['action'],
                    user_id=user.user_id,
                    id=dialog_manager.dialog_data['id'],
                    status_type='new',
                    status_msg=dialog_manager.dialog_data['status_msg'],
                    sell_or_buy_text=sell_or_buy_text,
                    username=get_username_or_link(user=user),
                    poker_id=user.poker_id,
                    rakeback_login=user.rakeback_login,
                    club_name=club.name,
                    club_id=club.id,
                    country=user.country,
                    request_data=dialog_manager.dialog_data['request_data'],
                    object=dialog_manager.dialog_data['object'],
                    amount=dialog_manager.dialog_data['amount'],
                    price=dialog_manager.dialog_data['price'],
                    sign=dialog_manager.dialog_data['sign'],
                    rub_value_str=dialog_manager.dialog_data['rub_value_str'],
                    buy_data=dialog_manager.dialog_data['buy_data'],
                    approve_or_reject_msg='',  # for edit
                    admin_username='',  # for edit
                    datetime_msg=await get_datetime(),
                ),
                reply_markup=confirm_kb(user_id=user.user_id, request_id=dialog_manager.dialog_data['request_id'])
            )

        else:
            await dialog_manager.event.bot.send_message(
                chat_id=settings.admin_chat_id,
                text=_(
                    text='REQUEST_DATA_FOR_ADMINS',
                    msg_type=dialog_manager.dialog_data['action'],
                    user_id=user.user_id,
                    id=dialog_manager.dialog_data['id'],
                    status_type='new',
                    status_msg=dialog_manager.dialog_data['status_msg'],
                    sell_or_buy_text=sell_or_buy_text,
                    username=get_username_or_link(user=user),
                    poker_id=user.poker_id,
                    rakeback_login=user.rakeback_login,
                    club_name=club.name,
                    club_id=club.id,
                    country=user.country,
                    request_data=dialog_manager.dialog_data['request_data'],
                    object=dialog_manager.dialog_data['object'],
                    amount=dialog_manager.dialog_data['amount'],
                    price=dialog_manager.dialog_data['price'],
                    sign=dialog_manager.dialog_data['sign'],
                    rub_value_str=dialog_manager.dialog_data['rub_value_str'],
                    buy_data=dialog_manager.dialog_data['buy_data'],
                    approve_or_reject_msg='',  # for edit
                    admin_username='',  # for edit
                    datetime_msg=await get_datetime(),
                ),
                reply_markup=confirm_kb(user_id=user.user_id, request_id=dialog_manager.dialog_data['request_id'])
            )

        dialog_manager.dialog_data['media_file_id'] = None  # clear media_file_id
        await callback.message.answer(text=_('ORDER_DATA_FOR_USER', id=dialog_manager.dialog_data['id']))
        await dialog_manager.switch_to(state=MarketStateGroup.request_is_done)


    @staticmethod
    async def input_any(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: str,
    ):
        await dialog_manager.start(state=MainMenuStateGroup.menu, mode=StartMode.RESET_STACK)


class RakebackCallbackHandler:
    @staticmethod
    async def buy_or_sell_crystals(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        if widget.widget_id == 'buy_crystals':
            dialog_manager.dialog_data['action'] = 'buy'
        elif widget.widget_id == 'sell_crystals':
            dialog_manager.dialog_data['action'] = 'sell'

        await dialog_manager.switch_to(state=RakebackStateGroup.input_login)


    @staticmethod
    async def entered_rakeback_login(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: str,
    ):
        dialog_manager.dialog_data['rakeback_login'] = value.strip()
        await dialog_manager.switch_to(state=RakebackStateGroup.input_amount)


    @staticmethod
    async def entered_crystals_amount(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: int,
    ):
        if value > 0:
            dialog_manager.dialog_data['amount'] = value

            # going to pick bank to buy or get card for sale
            if dialog_manager.dialog_data['action'] == 'buy':
                await dialog_manager.switch_to(state=RakebackStateGroup.pick_payment)
            elif dialog_manager.dialog_data['action'] == 'sell':
                await dialog_manager.switch_to(state=RakebackStateGroup.pick_crypto_or_card_for_sale)


    @staticmethod
    async def pick_bank(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str,
    ):
        dialog_manager.dialog_data['payment_method_id'] = item_id
        payment_method = await PaymentMethod.get(id=item_id)

        if payment_method.is_crypto:
            dialog_manager.dialog_data['is_crypto'] = True
        else:
            dialog_manager.dialog_data['is_crypto'] = False

        await dialog_manager.switch_to(state=RakebackStateGroup.input_payment_data)


    # pick crypto or card sale
    @staticmethod
    async def pick_crypto_or_card_for_sale(
            callback: CallbackQuery,
            widget: Button,
            dialog_manager: DialogManager,
    ):
        if callback.data == 'is_crypto_for_sale':
            dialog_manager.dialog_data['is_crypto_for_sale'] = True
            await dialog_manager.switch_to(state=RakebackStateGroup.input_payment_data)
        else:
            dialog_manager.dialog_data['is_crypto_for_sale'] = False
            await dialog_manager.switch_to(state=RakebackStateGroup.input_card_for_sale)


    # handle card for sale
    @staticmethod
    async def entered_card_for_sale(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: str,
    ):
        dialog_manager.dialog_data['card_for_sale'] = value
        await dialog_manager.switch_to(state=RakebackStateGroup.input_payment_data)


    # handle all 3 variants: 'buy bank', 'buy crypto', 'sell'
    @staticmethod
    async def entered_payment_data(
            message: Message,
            widget: MessageInput,
            dialog_manager: DialogManager,
    ):
        payment_method_id, media_file_id = None, None
        if dialog_manager.dialog_data['action'] == 'buy':
            payment_method_id = dialog_manager.dialog_data['payment_method_id']

            # handle photo for buy with card
            if not message.photo:
                return
            data = message.caption
            media_file_id = message.photo[-1].file_id
            dialog_manager.dialog_data['media_file_id'] = media_file_id

        else:
            if dialog_manager.dialog_data['is_crypto_for_sale']:
                data = message.text
            else:
                data = f'{dialog_manager.dialog_data["card_for_sale"]} {message.text}'

        request = await PaymentRequest.create(
            id=generate_random_string(),
            data=data,
            media_file_id=media_file_id,
            action=dialog_manager.dialog_data['action'],
            object=PaymentRequest.RequestObject.crystals,
            amount=dialog_manager.dialog_data['amount'],
            usd_price=dialog_manager.dialog_data['amount'],
            user_id=message.from_user.id,
            payment_method_id=payment_method_id,
        )

        dialog_manager.dialog_data['request_id'] = request.id
        await dialog_manager.switch_to(state=RakebackStateGroup.request_data)


    @staticmethod
    async def cancel_request(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        await PaymentRequest.filter(id=dialog_manager.dialog_data['request_id']).delete()
        await dialog_manager.switch_to(state=RakebackStateGroup.menu)


    @staticmethod
    async def send_request_to_admins(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        if dialog_manager.dialog_data['action'] == 'buy':
            sell_or_buy_text = 'Перевод от:'
        else:
            sell_or_buy_text = 'Заявка от:'

        user = await User.get(user_id=callback.from_user.id)
        user.rakeback_login = dialog_manager.dialog_data['rakeback_login']  # save rakeback_login
        await user.save()

        club = await user.club

        if dialog_manager.dialog_data.get('media_file_id'):
            await dialog_manager.event.bot.send_photo(
                chat_id=settings.admin_chat_id,
                photo=dialog_manager.dialog_data['media_file_id'],
                caption=_(
                    text='REQUEST_DATA_FOR_ADMINS',
                    msg_type=dialog_manager.dialog_data['action'],
                    user_id=user.user_id,
                    id=dialog_manager.dialog_data['id'],
                    status_type='new',
                    status_msg=dialog_manager.dialog_data['status_msg'],
                    sell_or_buy_text=sell_or_buy_text,
                    username=get_username_or_link(user=user),
                    poker_id=user.poker_id,
                    rakeback_login=user.rakeback_login,
                    club_name=club.name,
                    club_id=club.id,
                    country=user.country,
                    request_data=dialog_manager.dialog_data['request_data'],
                    object=dialog_manager.dialog_data['object'],
                    amount=dialog_manager.dialog_data['amount'],
                    price=dialog_manager.dialog_data['price'],
                    sign=dialog_manager.dialog_data['sign'],
                    rub_value_str=dialog_manager.dialog_data['rub_value_str'],
                    buy_data=dialog_manager.dialog_data['buy_data'],
                    approve_or_reject_msg='',  # for edit
                    admin_username='',  # for edit
                    datetime_msg=await get_datetime(),
                ),
                reply_markup=confirm_kb(user_id=user.user_id, request_id=dialog_manager.dialog_data['request_id'])
            )

        else:
            await dialog_manager.event.bot.send_message(
                chat_id=settings.admin_chat_id,
                text=_(
                    text='REQUEST_DATA_FOR_ADMINS',
                    msg_type=dialog_manager.dialog_data['action'],
                    user_id=user.user_id,
                    id=dialog_manager.dialog_data['id'],
                    status_type='new',
                    status_msg=dialog_manager.dialog_data['status_msg'],
                    sell_or_buy_text=sell_or_buy_text,
                    username=get_username_or_link(user=user),
                    poker_id=user.poker_id,
                    rakeback_login=user.rakeback_login,
                    club_name=club.name,
                    club_id=club.id,
                    country=user.country,
                    request_data=dialog_manager.dialog_data['request_data'],
                    object=dialog_manager.dialog_data['object'],
                    amount=dialog_manager.dialog_data['amount'],
                    price=dialog_manager.dialog_data['price'],
                    sign=dialog_manager.dialog_data['sign'],
                    rub_value_str=dialog_manager.dialog_data['rub_value_str'],
                    buy_data=dialog_manager.dialog_data['buy_data'],
                    approve_or_reject_msg='',  # for edit
                    admin_username='',  # for edit
                    datetime_msg=await get_datetime(),
                ),
                reply_markup=confirm_kb(user_id=user.user_id, request_id=dialog_manager.dialog_data['request_id'])
            )

        dialog_manager.dialog_data['media_file_id'] = None  # clear media_file_id
        await callback.message.answer(text=_('ORDER_DATA_FOR_USER', id=dialog_manager.dialog_data['id']))
        await dialog_manager.switch_to(state=RakebackStateGroup.request_is_done)


    @staticmethod
    async def input_any(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: str,
    ):
        await dialog_manager.start(state=MainMenuStateGroup.menu, mode=StartMode.RESET_STACK)

class CardsCallbackHandler:
    @staticmethod
    async def input_bank(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: str,
    ):
        dialog_manager.dialog_data['bank'] = value
        await dialog_manager.switch_to(state=CardsStateGroup.input_data)


    @staticmethod
    async def input_data(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: str,
    ):
        card = await PaymentMethod.create(
            name=dialog_manager.dialog_data['bank'],
            data=value,
        )

        dialog_manager.dialog_data['card_id'] = card.id
        await message.answer(text=_('CARD_IS_ADDED'))
        await dialog_manager.switch_to(state=CardsStateGroup.card_info)


    @staticmethod
    async def picked_card(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str,
    ):
        dialog_manager.dialog_data['card_id'] = item_id
        await dialog_manager.switch_to(state=CardsStateGroup.card_info)


    @staticmethod
    async def edit_card(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        payment_method = await PaymentMethod.get(id=dialog_manager.dialog_data['card_id'])
        if widget.widget_id == 'switch_is_active':
            if payment_method.is_active:
                payment_method.is_active = False
            else:
                payment_method.is_active = True

        elif widget.widget_id == 'switch_is_crypto':
            if payment_method.is_crypto:
                payment_method.is_crypto = False
            else:
                payment_method.is_crypto = True

        await payment_method.save()


    @staticmethod
    async def delete_card(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
       await PaymentMethod.filter(id=dialog_manager.dialog_data['card_id']).delete()
       await dialog_manager.switch_to(state=CardsStateGroup.menu)
