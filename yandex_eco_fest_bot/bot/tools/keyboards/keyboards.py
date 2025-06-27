from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from yandex_eco_fest_bot.bot import text_storage, static
from yandex_eco_fest_bot.bot.enums import MissionVerificationMethod, RequestStatus
from yandex_eco_fest_bot.bot.schemas import LocationMissionsStatus, AchievementStatus
from yandex_eco_fest_bot.bot.tools.factories import (
    MainMenuCallbackFactory,
    MissionCallbackFactory,
    RequestAnswerCallbackFactory,
    AchievementCallbackFactory,
    NoVerificationMissionCallbackFactory,
    CheckListOptionCallbackFactory,
    CheckListIsReadyCallbackFactory, NoVerificationWithDialogCallbackFactory, LikePictureCallbackFactory,
)
from yandex_eco_fest_bot.bot.tools.keyboards.button import Button
from yandex_eco_fest_bot.bot.tools.keyboards.button_storage import ButtonsStorage
from yandex_eco_fest_bot.bot.tools.keyboards.utils import (
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


def get_main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [ButtonsStorage.QUEST_BUTTON.get_button()],
        [ButtonsStorage.START_TEST_1.get_button()],
        [ButtonsStorage.MAIN_MAP.get_button()],
    ]

    if user_id in static.ADMIN_IDS:
        inline_keyboard.append([ButtonsStorage.ADMIN_BUTTON.get_button()])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_quest_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=ButtonsStorage.LOCATIONS_MAP.text,
        callback_data=ButtonsStorage.LOCATIONS_MAP.callback,
    )
    builder.button(
        text=ButtonsStorage.MY_PROGRES.text,
        callback_data=ButtonsStorage.MY_PROGRES.callback,
    )
    builder.button(
        text=ButtonsStorage.GO_TO_ACHIEVEMENTS_BUTTON.text,
        callback_data=ButtonsStorage.GO_TO_ACHIEVEMENTS_BUTTON.callback,
    )
    builder.button(
        text=text_storage.GO_BACK_TO_MAIN_MENU,
        callback_data=MainMenuCallbackFactory(),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_locations_menu_keyboard(
    locations: list[Location],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    locations.sort(key=lambda x: x.order)

    for location in locations:
        builder.button(
            text=location.name,
            callback_data=MissionCallbackFactory(
                id=location.id,
            ),
        )

    else:
        builder.button(
            text=text_storage.GO_BACK,
            callback_data=ButtonsStorage.QUEST_BUTTON.callback,
        )

    builder.adjust(1)
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
        callback_data=MainMenuCallbackFactory()
    )

    builder.adjust(1)
    return builder.as_markup()


async def get_specific_mission_keyboard(
    mission: Mission, status: RequestStatus | None
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if not status or status == RequestStatus.DECLINED:

        if mission.verification_method == MissionVerificationMethod.NO_VERIFICATION:
            builder.button(
                text=text_storage.I_VE_DONE_MISSION,
                callback_data=NoVerificationMissionCallbackFactory(
                    id=mission.id,
                ),
            )

        elif mission.verification_method == MissionVerificationMethod.NO_VERIFICATION_DIALOG:
            builder.button(
                text=text_storage.I_VE_DONE_MISSION_WITH_DIALOG,
                callback_data=NoVerificationWithDialogCallbackFactory(
                    id=mission.id,
                ),
            )

        elif mission.verification_method == MissionVerificationMethod.CHECK_LIST:
            check_list_keyboard = await get_check_list_keyboard(
                static.CHECK_LIST_QUESTIONS,
                [False] * len(static.CHECK_LIST_QUESTIONS),
                mission.id,
            )
            return check_list_keyboard

    builder.button(
        text=text_storage.GO_BACK,
        callback_data=ButtonsStorage.LOCATIONS_MAP.callback
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


async def get_check_list_keyboard(
    questions: list[str], is_completed: list[bool], mission_id: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for i, question in enumerate(questions):
        emoji = "✅" if is_completed[i] else "☑️"
        text = f"{question} {emoji}"

        builder.button(
            text=text,
            callback_data=CheckListOptionCallbackFactory(
                mission_id=mission_id,
                question_num=i,
                is_completed=is_completed[i],
            ),
        )

    builder.button(
        text=text_storage.I_VE_DONE_CHECK_LIST,
        callback_data=CheckListIsReadyCallbackFactory(
            mission_id=mission_id,
        ),
    )

    mission = await Mission.objects.get(id=mission_id)

    builder.button(
        text=text_storage.GO_BACK,
        callback_data=ButtonsStorage.LOCATIONS_MAP.callback
    )

    builder.adjust(1)
    return builder.as_markup()


def get_picture_rating_keyboard(user_mission_submission_id) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=text_storage.LIKE_PICTURE,
        callback_data=LikePictureCallbackFactory(
            user_mission_submission_id=user_mission_submission_id,
        ),
    )

    builder.adjust(1)
    return builder.as_markup()



def get_achievements_keyboard(
    achievement_display_schema: list[AchievementStatus]
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for achievement_status in achievement_display_schema:
        emoji = "✅" if achievement_status.is_succeeded else "☑️"
        text = f" {emoji} {achievement_status.achievement.name}"

        builder.button(
            text=text,
            callback_data=AchievementCallbackFactory(
                id=achievement_status.achievement.id
            ),
        )

    builder.button(
        text=text_storage.GO_BACK, callback_data=ButtonsStorage.QUEST_BUTTON.callback
    )

    builder.adjust(1)
    return builder.as_markup()


def get_back_to_quest_keyboard(text: str = text_storage.GO_BACK) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=text,
        callback_data=ButtonsStorage.QUEST_BUTTON.callback,
    )

    builder.adjust(1)
    return builder.as_markup()


def get_achievement_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=text_storage.GO_BACK,
        callback_data=ButtonsStorage.GO_TO_ACHIEVEMENTS_BUTTON.callback,
    )

    builder.adjust(1)
    return builder.as_markup()


def get_pretest_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Начать",
        callback_data=ButtonsStorage.START_TEST_2.callback,
    )

    builder.button(
        text="← Не сейчас",
        callback_data=MainMenuCallbackFactory(
            with_new_message=True,
            with_delete_markup=True,
            delete_message=True,
        ),
    )

    builder.adjust(1)
    return builder.as_markup()


def get_first_question_keyboard() -> InlineKeyboardMarkup:
    inline_keyboard = [[
        ButtonsStorage.OPTION_1_1.get_button(),
        ButtonsStorage.OPTION_1_2.get_button(),
        ButtonsStorage.OPTION_1_3.get_button(),
        ButtonsStorage.OPTION_1_4.get_button()]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_second_question_keyboard() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [ButtonsStorage.OPTION_2_1.get_button(),
        ButtonsStorage.OPTION_2_2.get_button(),
        ButtonsStorage.OPTION_2_3.get_button(),
        ButtonsStorage.OPTION_2_4.get_button()],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_third_question_keyboard() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [ButtonsStorage.OPTION_3_1.get_button(),
        ButtonsStorage.OPTION_3_2.get_button(),
        ButtonsStorage.OPTION_3_3.get_button(),
        ButtonsStorage.OPTION_3_4.get_button()],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def get_fourth_question_keyboard() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [ButtonsStorage.OPTION_4_1.get_button(),
        ButtonsStorage.OPTION_4_2.get_button(),
        ButtonsStorage.OPTION_4_3.get_button(),
        ButtonsStorage.OPTION_4_4.get_button()]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def get_fifth_question_keyboard() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [ButtonsStorage.OPTION_5_1.get_button(),
        ButtonsStorage.OPTION_5_2.get_button(),
        ButtonsStorage.OPTION_5_3.get_button(),
        ButtonsStorage.OPTION_5_4.get_button()]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)