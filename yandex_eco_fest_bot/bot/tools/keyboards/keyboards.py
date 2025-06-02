from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from yandex_eco_fest_bot.bot import text_storage
from yandex_eco_fest_bot.bot.enums import MissionVerificationMethod, RequestStatus
from yandex_eco_fest_bot.bot.schemas import LocationMissionsStatus, AchievementStatus
from yandex_eco_fest_bot.bot.tools.factories import (
    LocationCallbackFactory,
    LocationPageCallbackFactory,
    MainMenuCallbackFactory,
    MissionCallbackFactory,
    RequestAnswerCallbackFactory,
    AchievementCallbackFactory,
    AchievementPageCallbackFactory, NoVerificationMissionCallbackFactory,
)
from yandex_eco_fest_bot.bot.tools.keyboards.button import Button
from yandex_eco_fest_bot.bot.tools.keyboards.button_storage import ButtonsStorage
from yandex_eco_fest_bot.bot.tools.keyboards.utils import (
    LOCATIONS_PER_PAGE,
    get_page_number_by_location,
    get_mission_display_button,
)
from yandex_eco_fest_bot.db.tables import Location, Mission, Achievement


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
    delete_message: bool = False,
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


def get_locations_menu_keyboard(
    locations: list[Location],
    page_number: int = 1,
    back_to_locations_parent: Location = None,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    locations.sort(key=lambda x: x.order)
    paginated_locations = get_paginated_objects(
        locations, page_number, LOCATIONS_PER_PAGE
    )

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

    extra_buttons = (
        int(page_number > 1)
        + 1
        + int(page_number < len(locations) // LOCATIONS_PER_PAGE + 1)
    )

    builder.adjust(*[1] * len(paginated_locations), extra_buttons)
    return builder.as_markup()


def get_missions_keyboard(
    mission_display_schema: LocationMissionsStatus,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    missions_statuses = mission_display_schema.missions
    for mission_status in missions_statuses:
        builder.button(
            text=get_mission_display_button(mission_status),
            callback_data=MissionCallbackFactory(
                id=mission_status.mission.id,
            ),
        )

    builder.button(
        text=text_storage.GO_BACK,
        callback_data=LocationPageCallbackFactory(
            page=get_page_number_by_location(mission_display_schema.location),
        ),
    )

    builder.adjust(1)
    return builder.as_markup()


def get_specific_mission_keyboard(mission: Mission, status: RequestStatus) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if not status or status == RequestStatus.DECLINED:

        if mission.verification_method == MissionVerificationMethod.NO_VERIFICATION:
            builder.button(
                text=text_storage.I_VE_DONE_MISSION,
                callback_data=NoVerificationMissionCallbackFactory(
                    id=mission.id,
                ),
            )

    builder.button(
        text=text_storage.GO_BACK,
        callback_data=LocationCallbackFactory(
            id=mission.location_id,
            with_new_message=False,
        ),
    )

    builder.adjust(1)
    return builder.as_markup()


def get_cancel_state_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=text_storage.CANCEL,
        callback_data=MainMenuCallbackFactory(
            with_new_message=True,
            delete_message=True,
        ),
    )

    builder.adjust(1)
    return builder.as_markup()


def get_submission_options_keyboard(request_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=text_storage.ACCEPT_SUBMISSION,
        callback_data=RequestAnswerCallbackFactory(
            request_id=request_id,
            is_accepted=True,
        ),
    )

    builder.button(
        text=text_storage.REJECT_SUBMISSION,
        callback_data=RequestAnswerCallbackFactory(
            request_id=request_id,
            is_accepted=False,
        ),
    )

    builder.adjust(1)
    return builder.as_markup()


def get_go_to_achievements_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=ButtonsStorage.GO_TO_ACHIEVEMENTS_BUTTON.text,
        callback_data=ButtonsStorage.GO_TO_ACHIEVEMENTS_BUTTON.callback,
    )
    builder.button(
        text=text_storage.GO_BACK_TO_MAIN_MENU, callback_data=MainMenuCallbackFactory()
    )

    builder.adjust(1)

    return builder.as_markup()


def get_achievements_keyboard(
    achievement_display_schema: list[AchievementStatus], page_num: int = 1
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if page_num == 1:
        achievements = achievement_display_schema[:6]
    else:
        achievements = achievement_display_schema[6:]

    for achievement_status in achievements:
        emoji = "✅" if achievement_status.is_succeeded else "☑️"
        text = f" {emoji} {achievement_status.achievement.name}"

        builder.button(
            text=text,
            callback_data=AchievementCallbackFactory(
                id=achievement_status.achievement.id
            ),
        )

    if page_num == 1:
        page_btn_text = text_storage.NEXT_PAGE
        page_btn_callback = AchievementPageCallbackFactory(page=2)

        builder.button(
            text=text_storage.GO_BACK, callback_data=ButtonsStorage.MY_PROGRES.callback
        )

        builder.button(
            text=page_btn_text,
            callback_data=page_btn_callback,
        )
    else:
        page_btn_text = text_storage.PREV_PAGE
        page_btn_callback = AchievementPageCallbackFactory(page=1)

        builder.button(
            text=page_btn_text,
            callback_data=page_btn_callback,
        )

        builder.button(
            text=text_storage.GO_BACK, callback_data=ButtonsStorage.MY_PROGRES.callback
        )

    builder.adjust(*[1] * 6, 2)
    return builder.as_markup()


def get_achievement_keyboard(achievement: Achievement) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    page_num = 1 if achievement.id <= 6 else 2

    builder.button(
        text=text_storage.GO_BACK,
        callback_data=AchievementPageCallbackFactory(
            page=page_num,
        ),
    )

    builder.adjust(1)
    return builder.as_markup()
