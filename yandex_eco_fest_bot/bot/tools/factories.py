from aiogram.filters.callback_data import CallbackData


class MainMenuCallbackFactory(CallbackData, prefix="main_menu_callback_factory"):
    with_new_message: bool = False
    with_delete_markup: bool = False
    delete_message: bool = False


class LocationCallbackFactory(CallbackData, prefix="location_callback_factory"):
    id: int
    with_new_message: bool = True


class LocationPageCallbackFactory(CallbackData, prefix="location_page_callback_factory"):
    page: int


class MissionCallbackFactory(CallbackData, prefix="mission_callback_factory"):
    id: int


class RequestAnswerCallbackFactory(CallbackData, prefix="request_answer_callback_factory"):
    request_id: int
    is_accepted: bool


class AchievementCallbackFactory(CallbackData, prefix="achievement_callback_factory"):
    id: int


class AchievementPageCallbackFactory(CallbackData, prefix="achievement_page_callback_factory"):
    page: int
