import logging

from aiogram import Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from yandex_eco_fest_bot.bot import text_storage
from yandex_eco_fest_bot.bot.tools.factories import LocationPageCallbackFactory, MainMenuCallbackFactory, \
    LocationCallbackFactory, MissionCallbackFactory
# from yandex_eco_fest_bot.bot.tools.filters import MainMenuFilter
from yandex_eco_fest_bot.bot.tools.keyboards.button_storage import ButtonsStorage
from yandex_eco_fest_bot.bot.tools.keyboards.keyboards import get_main_menu_keyboard, get_go_to_main_menu_keyboard, \
    get_one_button_keyboard, get_locations_menu_keyboard, get_missions_keyboard, get_specific_mission_keyboard
from yandex_eco_fest_bot.bot.utils import send_locations_with_image, get_location_info_text, get_mission_info_text
from yandex_eco_fest_bot.db.tables import User, Location, Mission

dp = Dispatcher()
router = Router()
dp.include_router(router)

logger = logging.getLogger(__name__)


@dp.message(CommandStart())
async def handle_start_command(message: Message):

    # todo: check username

    await User.objects.get_or_create(
        id=message.from_user.id,
        defaults={"username": message.from_user.username}
    )

    await message.answer(
        text_storage.START_TEXT,
        reply_markup=get_one_button_keyboard(button=ButtonsStorage.AFTER_START_BUTTON))


@router.callback_query(F.data == ButtonsStorage.AFTER_START_BUTTON.callback)
async def handle_after_start_callback(call: CallbackQuery):
    await call.message.edit_text(
        text_storage.AFTER_START_TEXT.format(name=call.from_user.first_name),
        reply_markup=get_go_to_main_menu_keyboard(button_text="Поехали!")
    )


@router.callback_query(
    MainMenuCallbackFactory.filter()
)
async def handle_main_menu_callback(call: CallbackQuery, callback_data: MainMenuCallbackFactory):
    if callback_data.delete_message:
        await call.message.delete()

    if callback_data.with_delete_markup:
        await call.message.edit_reply_markup(reply_markup=None)

    if callback_data.with_new_message:
        await call.message.answer(
            text=text_storage.MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await call.message.edit_text(
        text=text_storage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(Command("menu"))
async def handle_main_menu_command(message: Message):
    await message.answer(
        text=text_storage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )


@router.callback_query(F.data == ButtonsStorage.LOCATIONS_MAP.callback)
async def handle_location_map_callback(call: CallbackQuery):
    await call.message.delete()
    locations = await Location.objects.filter(parent=None).all()
    await send_locations_with_image(call, locations)


@router.callback_query(
    LocationPageCallbackFactory.filter()
)
async def handle_location_page_callback(call: CallbackQuery, callback_data: LocationPageCallbackFactory):
    locations = await Location.objects.filter(parent=None).all()
    await call.message.edit_reply_markup(
        reply_markup=get_locations_menu_keyboard(locations, page_number=callback_data.page)
    )


@router.callback_query(
    LocationCallbackFactory.filter()
)
async def handle_location_callback(call: CallbackQuery, callback_data: LocationCallbackFactory):

    location = await Location.objects.get(id=callback_data.id)
    text = get_location_info_text(location)

    if location.is_group:
        locations = await Location.objects.filter(parent=location).all()
        reply_markup = get_locations_menu_keyboard(locations, back_to_locations_parent=location)
    else:
        reply_markup = get_missions_keyboard(location)

    kwargs = {
        "text": text,
        "reply_markup": reply_markup,
        "parse_mode": ParseMode.HTML
    }

    if not callback_data.with_new_message:
        await call.message.edit_text(**kwargs)
        return

    await call.message.delete()
    await call.message.answer(**kwargs)


@router.callback_query(
    MissionCallbackFactory.filter()
)
async def handle_mission_callback(call: CallbackQuery, callback_data: MissionCallbackFactory):

    mission = await Mission.objects.get(id=callback_data.id)
    text = get_mission_info_text(mission)

    await call.message.edit_text(
        text=text,
        reply_markup=get_specific_mission_keyboard(mission),
        parse_mode=ParseMode.HTML
    )
