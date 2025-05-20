from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from yandex_eco_fest_bot.bot import text_storage
from yandex_eco_fest_bot.bot.tools.factories import LocationCallbackFactory, LocationPageCallbackFactory, \
    MainMenuCallbackFactory, MissionCallbackFactory
from yandex_eco_fest_bot.bot.tools.keyboards.button import Button
from yandex_eco_fest_bot.bot.tools.keyboards.button_storage import ButtonsStorage
from yandex_eco_fest_bot.bot.tools.keyboards.utils import LOCATIONS_PER_PAGE, get_page_number_by_location
from yandex_eco_fest_bot.db.tables import Location, Mission


def get_paginated_objects(objects: list, page_number: int, page_size: int) -> list:
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    return objects[start_index:end_index]


def get_one_button_keyboard(button: Button, button_text=None) -> InlineKeyboardMarkup:
    button = button.get_button(text=button_text) if button_text else button.get_button()
    inline_keyboard = [[button]]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_go_to_main_menu_keyboard(
    button_text: str = text_storage.GO_TO_MAIN_MENU,
    with_new_message: bool = False,
    with_delete_markup: bool = False,
    delete_message: bool = False
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=button_text,
        callback_data=MainMenuCallbackFactory(
            with_new_message=with_new_message,
            with_delete_markup=with_delete_markup,
            delete_message=delete_message,
        ),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [ButtonsStorage.LOCATIONS_MAP.get_button()],
        [ButtonsStorage.MY_PROGRES.get_button()],
        [ButtonsStorage.TEAM_PROGRES.get_button()],
        [ButtonsStorage.HELP.get_button()],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_locations_menu_keyboard(locations: list[Location], page_number: int = 1, back_to_locations_parent: Location = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    locations.sort(key=lambda x: x.order)
    paginated_locations = get_paginated_objects(locations, page_number, LOCATIONS_PER_PAGE)

    for location in paginated_locations:
        builder.button(
            text=location.name,
            callback_data=LocationCallbackFactory(
                id=location.id,
            ),
        )

    if page_number > 1:
        builder.button(
            text=text_storage.PREV_PAGE,
            callback_data=LocationPageCallbackFactory(
                page=page_number - 1,
            ),
        )

    if back_to_locations_parent:
        builder.button(
            text=text_storage.GO_BACK,
            callback_data=LocationPageCallbackFactory(
                page=get_page_number_by_location(back_to_locations_parent),
            ),
        )
    else:
        builder.button(
            text=text_storage.GO_TO_MAIN_MENU_SHORT,
            callback_data=MainMenuCallbackFactory(
                with_new_message=True,
                delete_message=True,
            ),
        )

    if page_number < len(locations) // LOCATIONS_PER_PAGE + 1:
        builder.button(
            text=text_storage.NEXT_PAGE,
            callback_data=LocationPageCallbackFactory(
                page=page_number + 1,
            ),
        )

    extra_buttons = int(page_number > 1) + 1 + int(page_number < len(locations) // LOCATIONS_PER_PAGE + 1)

    builder.adjust(*[1] * len(paginated_locations), extra_buttons)
    return builder.as_markup()


def get_missions_keyboard(location: Location) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    missions = location.missions
    for mission in missions:
        builder.button(
            text=mission.name,
            callback_data=MissionCallbackFactory(
                id=mission.id,
            ),
        )

    builder.button(
        text=text_storage.GO_BACK,
        callback_data=LocationPageCallbackFactory(
            page=get_page_number_by_location(location),
        ),
    )

    builder.adjust(1)
    return builder.as_markup()


def get_specific_mission_keyboard(mission: Mission) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=text_storage.GO_BACK,
        callback_data=LocationCallbackFactory(
            id=mission.location_id,
            with_new_message=False,
        )
    )

    builder.adjust(1)
    return builder.as_markup()
