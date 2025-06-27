from aiogram.filters.callback_data import CallbackData


class MainMenuCallbackFactory(CallbackData, prefix="main_menu_callback_factory"):
    with_new_message: bool = False
    with_delete_markup: bool = False
    delete_message: bool = False


class LocationCallbackFactory(CallbackData, prefix="location_callback_factory"):
    id: int
    with_new_message: bool = True


class MissionCallbackFactory(CallbackData, prefix="mission_callback_factory"):
    id: int


class NoVerificationMissionCallbackFactory(
    CallbackData, prefix="no_verification_mission_callback_factory"
):
    id: int


class NoVerificationWithDialogCallbackFactory(
    CallbackData, prefix="no_verification_with_dialog_callback_factory"
):
    id: int


class LikePictureCallbackFactory(
    CallbackData, prefix="like_picture_callback_factory"
):
    user_mission_submission_id: int


class RequestAnswerCallbackFactory(
    CallbackData, prefix="request_answer_callback_factory"
):
    request_id: int
    is_accepted: bool


class AchievementCallbackFactory(CallbackData, prefix="achievement_callback_factory"):
    id: int


class CheckListOptionCallbackFactory(
    CallbackData, prefix="check_list_callback_factory"
):
    mission_id: int
    question_num: int
    is_completed: bool


class CheckListIsReadyCallbackFactory(
    CallbackData, prefix="check_list_is_ready_callback_factory"
):
    mission_id: int
