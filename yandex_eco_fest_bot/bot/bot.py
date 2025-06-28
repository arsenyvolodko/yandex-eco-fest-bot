import logging

from aiogram import Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder

from yandex_eco_fest_bot.bot import text_storage, static
from yandex_eco_fest_bot.bot.enums import RequestStatus, MissionVerificationMethod
from yandex_eco_fest_bot.bot.static import CAPTION_TYPE_VERIFICATION_METHODS
from yandex_eco_fest_bot.bot.text_storage import PRE_TEST_TEXT
from yandex_eco_fest_bot.bot.tools import states
from yandex_eco_fest_bot.bot.tools.factories import (
    MainMenuCallbackFactory,
    MissionCallbackFactory,
    RequestAnswerCallbackFactory,
    AchievementCallbackFactory,
    NoVerificationMissionCallbackFactory,
    CheckListOptionCallbackFactory,
    CheckListIsReadyCallbackFactory,
    NoVerificationWithDialogCallbackFactory,
    LikePictureCallbackFactory,
)
from yandex_eco_fest_bot.bot.tools.keyboards.button_storage import ButtonsStorage
from yandex_eco_fest_bot.bot.tools.keyboards.keyboards import (
    get_main_menu_keyboard,
    get_go_to_main_menu_keyboard,
    get_one_button_keyboard,
    get_locations_menu_keyboard,
    get_missions_keyboard,
    get_specific_mission_keyboard,
    get_cancel_state_keyboard,
    get_achievement_keyboard,
    get_submission_options_keyboard,
    get_check_list_keyboard,
    get_picture_rating_keyboard, get_first_question_keyboard, get_second_question_keyboard, get_third_question_keyboard,
    get_fourth_question_keyboard, get_fifth_question_keyboard, get_quest_menu_keyboard, get_back_to_quest_keyboard,
    get_achievements_keyboard, get_pretest_keyboard, get_after_test_keyboard, get_confirm_feedback_keyboard,
    get_last_keyboard,
)
from yandex_eco_fest_bot.bot.utils import (
    get_location_info_text,
    get_state_by_verification_method,
    VERIFICATION_METHOD_TO_STATE,
    save_request_to_redis,
    get_missions_with_score,
    get_user_achievements,
    resend_submission_photo_util,
    resend_submission_text_util,
    resend_submission_voice_util,
    check_verification_code,
    process_verification_code_submission,
    get_mission_task_text,
    edit_photo_message,
    send_photo_message,
    get_location_media_url,
    get_achievement_media_url, send_start_achievement, check_achievement_updates, get_score_name,
)
from yandex_eco_fest_bot.core.redis_config import r
from yandex_eco_fest_bot.db.tables import (
    User,
    Location,
    Mission,
    UserMissionSubmission,
    Achievement,
    UserAchievement, UserTest,
)

dp = Dispatcher()
router = Router()
dp.include_router(router)

logger = logging.getLogger(__name__)


@dp.message(CommandStart())
async def handle_start_command(message: Message):
    # todo: check username

    await User.objects.get_or_create(
        id=message.from_user.id, defaults={"username": message.from_user.username}
    )

    await message.answer(
        text_storage.START_TEXT,
        reply_markup=get_one_button_keyboard(button=ButtonsStorage.AFTER_START_BUTTON),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == ButtonsStorage.AFTER_START_BUTTON.callback)
async def handle_after_start_callback(call: CallbackQuery):
    if call.from_user.first_name:
        name = f" {call.from_user.first_name}"
    else:
        name = ""

    await call.message.edit_reply_markup(
        reply_markup=None
    )

    media_group = MediaGroupBuilder()
    media_group.add_photo(
        media=static.BIG_MAP_MEDIA_URL,
    )
    media_group.add_photo(
        media=static.PROGRAM_MEDIA_URL
    )

    await call.message.answer_media_group(
        media_group.build(),
    )

    await call.message.answer(
        text=text_storage.MAIN_MAP_TEXT,
        reply_markup=get_one_button_keyboard(
            ButtonsStorage.THANKS_BUTTON,
        ),
        parse_mode = ParseMode.HTML,
    )

# MAIN_MAP

@router.callback_query(F.data == ButtonsStorage.MAIN_MAP.callback)
async def handle_after_start_callback(call: CallbackQuery):
    await edit_photo_message(
        call.bot,
        message=call.message,
        photo_url=static.BIG_MAP_MEDIA_URL,
        caption=None,
        reply_markup=get_go_to_main_menu_keyboard(text_storage.GO_BACK_TO_MAIN_MENU)
    )


@router.callback_query(F.data == ButtonsStorage.THANKS_BUTTON.callback)
async def handle_after_start_callback(call: CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.answer(
        text_storage.INTRO_TEXT,
        reply_markup=get_go_to_main_menu_keyboard(button_text="Поехали!", with_delete_markup=True, with_new_message=True),
        parse_mode = ParseMode.HTML,
    )


@router.callback_query(F.data == ButtonsStorage.HIDE_MESSAGE.callback)
async def handle_after_start_callback(call: CallbackQuery):
    await call.message.delete()


@router.callback_query(F.data == ButtonsStorage.FEED_BACK_1.callback)
async def handle_after_start_callback(call: CallbackQuery):
    await call.message.edit_reply_markup(
        reply_markup=get_confirm_feedback_keyboard()
    )


@router.callback_query(F.data == ButtonsStorage.FEED_BACK_2.callback)
async def handle_after_start_callback(call: CallbackQuery):

    await call.message.delete()
    await call.message.answer("Отправляю..")

    users = await User.objects.all()

    for user in users:
        try:
            await call.bot.send_message(
                chat_id=user.id,
                text=text_storage.END_TEXT,
                reply_markup=get_last_keyboard(),
            )
        except Exception:
            pass

    await call.message.answer(
        text="Сообщение успешно разослано всем пользователям!"
    )


@router.callback_query(F.data == ButtonsStorage.GET_START_ACHIEVEMENT.callback)
async def handle_get_first_achievement_callback(call: CallbackQuery):
    await call.message.edit_reply_markup(
        reply_markup=None
    )
    achievement = await Achievement.objects.filter(id=1).get()
    await UserAchievement.objects.get_or_create(
        user_id=call.from_user.id,
        achievement_id=achievement.id,
    )
    await send_start_achievement(call.bot, call.from_user.id, achievement)


@router.callback_query(MainMenuCallbackFactory.filter())
async def handle_main_menu_callback(
    call: CallbackQuery, callback_data: MainMenuCallbackFactory, state: FSMContext
):
    state_data = await state.get_data()
    if msg_id := state_data.get("msg_id"):
        await call.bot.edit_message_reply_markup(
            chat_id=call.from_user.id, message_id=msg_id, reply_markup=None
        )

    await state.clear()

    if callback_data.delete_message:
        # todo: safe delete func
        try:
            await call.message.delete()
        except Exception:
            pass

    if callback_data.with_delete_markup:
        try:
            await call.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

    if callback_data.with_new_message:
        await send_photo_message(
            call.bot,
            call.message.chat.id,
            photo_url=static.MAIN_MENU_MEDIA_URL,
            caption=text_storage.MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(call.from_user.id),
        )
        return

    await edit_photo_message(
        call.bot,
        call.message,
        static.MAIN_MENU_MEDIA_URL,
        caption=text_storage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(call.from_user.id),
    )


@router.message(Command("menu"))
async def handle_main_menu_command(message: Message):
    await send_photo_message(
        message.bot,
        message.chat.id,
        photo_url=static.MAIN_MENU_MEDIA_URL,
        caption=text_storage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(message.from_user.id),
    )


@router.callback_query(F.data == ButtonsStorage.ADMIN_BUTTON.callback)
async def handle_admin_button_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()

    if call.from_user.id not in static.ADMIN_IDS:
        await call.answer(text="У вас недостаточно прав", show_alert=True)
        return

    await call.message.delete()

    await call.message.answer(
        text="Введи текст сообщения которое отправить всем. Можно добавить одно фото, но важно, чтобы это было в одном сообщении. Используй именно фото, а не файл с фото.",
        reply_markup=get_cancel_state_keyboard()
    )

    await state.set_state(states.WAITING_FOR_ADMIN_MESSAGE)

# Locations


@router.callback_query(F.data == ButtonsStorage.QUEST_BUTTON.callback)
async def handle_location_map_callback(call: CallbackQuery):
    reply_markup = get_quest_menu_keyboard()
    await edit_photo_message(
        call.bot,
        message=call.message,
        photo_url=static.MAIN_MENU_MEDIA_URL,
        caption=text_storage.LOCATIONS_MAP_TEXT,
        reply_markup=reply_markup,
    )


@router.callback_query(F.data == ButtonsStorage.LOCATIONS_MAP.callback)
async def handle_location_map_callback(call: CallbackQuery):
    locations = await Location.objects.filter(parent=None).all()
    reply_markup = get_locations_menu_keyboard(locations)
    await edit_photo_message(
        call.bot,
        message=call.message,
        photo_url=static.MAIN_MAP_MEDIA_URL,
        caption=text_storage.LOCATIONS_MAP_TEXT,
        reply_markup=reply_markup,
    )

@router.callback_query(MissionCallbackFactory.filter())
async def handle_mission_callback(
    call: CallbackQuery, callback_data: MissionCallbackFactory, state: FSMContext
):
    await state.clear()

    mission = await Mission.objects.get(id=callback_data.id)
    old_submission: UserMissionSubmission = await UserMissionSubmission.objects.filter(
        mission_id=mission.id
    ).first()
    status = old_submission.status if old_submission else None

    text = await get_mission_task_text(mission, old_submission)

    if not old_submission or status == RequestStatus.DECLINED:

        verification_method = mission.verification_method
        if verification_method in VERIFICATION_METHOD_TO_STATE:
            new_state = get_state_by_verification_method(mission.verification_method)
            await state.set_state(new_state)
            await state.set_data(
                {
                    "mission_id": mission.id,
                    "msg_id": call.message.message_id,
                }
            )

    reply_markup = await get_specific_mission_keyboard(mission, status)

    await edit_photo_message(
        call.bot,
        message=call.message,
        photo_url=get_location_media_url(mission.location),
        caption=text,
        reply_markup=reply_markup,
    )


@router.callback_query(NoVerificationMissionCallbackFactory.filter())
async def handle_no_verification_mission_callback(
    call: CallbackQuery, callback_data: NoVerificationMissionCallbackFactory
):
    mission = await Mission.objects.get(id=callback_data.id)
    old_submission: UserMissionSubmission = await UserMissionSubmission.objects.filter(
        mission_id=mission.id, user_id=call.from_user.id
    ).first()

    if old_submission and old_submission.status == RequestStatus.ACCEPTED:
        await edit_photo_message(
            call.bot,
            message=call.message,
            photo_url=get_location_media_url(mission.location),
            caption=text_storage.MISSION_ALREADY_ACCEPTED_ALERT,
            reply_markup=get_go_to_main_menu_keyboard(
                text_storage.GO_BACK_TO_MAIN_MENU,
                with_new_message=True,
                with_delete_markup=True,
            ),
        )
        return

    await UserMissionSubmission.objects.create(
        user_id=call.from_user.id,
        mission_id=mission.id,
        status=RequestStatus.ACCEPTED,
    )
    await check_achievement_updates(call.bot, call.from_user.id)

    await edit_photo_message(
        call.bot,
        message=call.message,
        photo_url=get_location_media_url(mission.location),
        caption=text_storage.NO_VERIFICATION_AND_CHECK_LIST_MISSION_ACCEPTED_INFO.format(
            mission_name=mission.name,
            mission_score=mission.score,
            mission_description=mission.description,
        ),
        reply_markup=get_go_to_main_menu_keyboard(
            button_text=text_storage.GREAT,
            with_new_message=True,
            with_delete_markup=True,
        ),
    )


@router.callback_query(CheckListOptionCallbackFactory.filter())
async def handle_checklist_mission_callback(
    call: CallbackQuery, callback_data: CheckListOptionCallbackFactory
):
    reply_markup = call.message.reply_markup
    inline_keyboard = reply_markup.inline_keyboard
    is_completed_list = []

    for i in inline_keyboard:
        text = i[0].text
        is_completed = text[-1] == "✅"
        is_completed_list.append(is_completed)

    is_completed_list[callback_data.question_num] = not callback_data.is_completed

    new_reply_markup = await get_check_list_keyboard(
        static.CHECK_LIST_QUESTIONS, is_completed_list, callback_data.mission_id
    )

    mission = await Mission.objects.get(id=callback_data.mission_id)
    text = await get_mission_task_text(mission, None)

    await edit_photo_message(
        call.bot,
        message=call.message,
        photo_url=get_location_media_url(mission.location),
        caption=text,
        reply_markup=new_reply_markup,
    )


@router.callback_query(NoVerificationWithDialogCallbackFactory.filter())
async def handle_mission_with_dialog_callback(
    call: CallbackQuery,
    callback_data: NoVerificationWithDialogCallbackFactory,
    state: FSMContext,
):
    mission = await Mission.objects.get(id=callback_data.id)
    old_submission: UserMissionSubmission = await UserMissionSubmission.objects.filter(
        mission_id=mission.id, user_id=call.from_user.id
    ).first()

    if old_submission and old_submission.status == RequestStatus.ACCEPTED:
        await call.message.edit_text(
            text=text_storage.MISSION_ALREADY_ACCEPTED_ALERT,
            reply_markup=get_go_to_main_menu_keyboard(
                text_storage.GO_BACK_TO_MAIN_MENU,
                with_new_message=True,
                with_delete_markup=True,
            ),
            parse_mode=ParseMode.HTML,
        )
        return

    await state.clear()
    await state.set_state(states.WAITING_FOR_ROBOT_PHOTO)
    await state.set_data({"mission_id": mission.id})
    await edit_photo_message(
        call.bot,
        message=call.message,
        photo_url=get_location_media_url(mission.location),
        caption=None,
    )
    await call.message.answer(
        text=text_storage.SEND_ROBOT_PIC,
    )


@router.callback_query(CheckListIsReadyCallbackFactory.filter())
async def evaluate_check_list_score_callback(
    call: CallbackQuery, callback_data: CheckListIsReadyCallbackFactory
):
    mission = await Mission.objects.get(id=callback_data.mission_id)

    old_submission: UserMissionSubmission = await UserMissionSubmission.objects.filter(
        mission_id=mission.id, user_id=call.from_user.id
    ).first()

    if old_submission and old_submission.status == RequestStatus.ACCEPTED:
        await call.message.edit_text(
            text=text_storage.MISSION_ALREADY_ACCEPTED_ALERT,
            reply_markup=get_go_to_main_menu_keyboard(
                text_storage.GO_BACK_TO_MAIN_MENU,
            ),
            parse_mode=ParseMode.HTML,
        )
        return

    reply_markup = call.message.reply_markup
    inline_keyboard = reply_markup.inline_keyboard
    is_completed_list = []

    for i in inline_keyboard:
        text = i[0].text
        is_completed = text[-1] == "✅"
        is_completed_list.append(is_completed)

    score = is_completed_list.count(True) * static.CHECK_LIST_POINT_SCORE
    await UserMissionSubmission.objects.create(
        user_id=call.from_user.id,
        mission_id=mission.id,
        status=RequestStatus.ACCEPTED,
        extra_score=score,
    )
    await check_achievement_updates(call.bot, call.from_user.id)

    await edit_photo_message(
        call.bot,
        message=call.message,
        photo_url=get_location_media_url(mission.location),
        caption=text_storage.NO_VERIFICATION_AND_CHECK_LIST_MISSION_ACCEPTED_INFO.format(
            mission_name=mission.name,
            mission_score=score,
            mission_description=mission.description,
        ),
        reply_markup=get_go_to_main_menu_keyboard(
            button_text=text_storage.GREAT,
        ),
    )


async def check_old_submissions(
    message: Message, mission_id: int, verification_method: MissionVerificationMethod
) -> bool:
    if not mission_id:

        if verification_method == MissionVerificationMethod.PHOTO:
            await message.answer(
                text=text_storage.CANNOT_HANDLE_SEVERAL_PHOTOS,
            )
            return False

        await message.answer(
            text=text_storage.SOMETHING_WENT_WRONG,
            reply_markup=get_go_to_main_menu_keyboard(
                text_storage.GO_BACK_TO_MAIN_MENU
            ),
        )

        return False

    mission = await Mission.objects.get(id=mission_id)

    old_submission = await UserMissionSubmission.objects.filter(
        user_id=message.from_user.id, mission_id=mission.id
    ).first()

    if old_submission:
        if old_submission.status == RequestStatus.ACCEPTED:
            await message.answer(
                text=text_storage.MISSION_ALREADY_ACCEPTED_ALERT,
                reply_markup=get_go_to_main_menu_keyboard(
                    text_storage.GO_BACK_TO_MAIN_MENU,
                    with_new_message=True,
                    with_delete_markup=True,
                ),
            )

            return False

        elif old_submission.status == RequestStatus.PENDING:
            await message.answer(
                text=text_storage.MISSION_IN_PROGRESS_ALERT,
                reply_markup=get_go_to_main_menu_keyboard(
                    text_storage.GO_BACK_TO_MAIN_MENU,
                    with_new_message=True,
                    with_delete_markup=True,
                ),
            )

            return False

        await old_submission.delete()

    return True


async def handle_verification_code_mission(
    user: User, mission: Mission, message: Message, msg_id: int, state: FSMContext
):
    success = check_verification_code(mission, message.text)
    answer = await process_verification_code_submission(mission, user.id, success)
    await message.bot.edit_message_reply_markup(
        chat_id=message.from_user.id, message_id=msg_id, reply_markup=None
    )
    if success:
        await state.clear()
        await check_achievement_updates(message.bot, user.id)
        await message.answer(
            text=answer,
            reply_markup=get_go_to_main_menu_keyboard(
                button_text=text_storage.GREAT,
            ),
            parse_mode=ParseMode.HTML,
        )
    else:
        message = await message.answer(
            text=answer,
            reply_markup=get_go_to_main_menu_keyboard(
                button_text=text_storage.GO_BACK_TO_MAIN_MENU,
            ),
            parse_mode=ParseMode.HTML,
        )
        await state.set_data(
            {
                "mission_id": mission.id,
                "msg_id": message.message_id,
            }
        )

    return


async def handle_submission_util(
    message: Message, state: FSMContext, verification_method: MissionVerificationMethod
):
    state_data = await state.get_data()
    mission_id = state_data.get("mission_id")
    msg_id = state_data.get("msg_id")

    success = await check_old_submissions(message, mission_id, verification_method)
    if not success:
        return

    mission = await Mission.objects.get(id=mission_id)
    location = await Location.objects.get(id=mission.location_id)
    user = await User.objects.get(id=message.from_user.id)

    if verification_method == MissionVerificationMethod.VERIFICATION_CODE:
        await handle_verification_code_mission(user, mission, message, msg_id, state)
        return

    user_mission_submission = await UserMissionSubmission.objects.create(
        user_id=user.id,
        mission_id=mission.id,
    )

    text = text_storage.SUBMISSION_REQUEST_TEXT.format(
        username=user.username,
        mission_name=mission.name,
    )

    resend_kwargs = {
        "chat_id": location.chat_id,
        "reply_markup": get_submission_options_keyboard(user_mission_submission.id),
        "parse_mode": ParseMode.HTML,
    }

    if verification_method == MissionVerificationMethod.PHOTO:
        await state.clear()
        file_id = message.photo[-1].file_id
        await resend_submission_photo_util(message.bot, text, file_id, **resend_kwargs)
    elif (
        verification_method == MissionVerificationMethod.VOICE
        or verification_method == MissionVerificationMethod.VIDEO
    ):
        await state.clear()
        file_id = message.voice.file_id if message.voice else message.video_note.file_id
        await resend_submission_voice_util(message.bot, text, file_id, resend_kwargs)
    elif verification_method == MissionVerificationMethod.TEXT:
        await state.clear()
        text = (
            f"{text}\n\nПользователь отправил следующий текст:\n«<b>{message.text}</b>»"
        )
        await resend_submission_text_util(message.bot, text, resend_kwargs)

    await message.bot.edit_message_reply_markup(
        chat_id=message.from_user.id, message_id=msg_id, reply_markup=None
    )

    message = await message.answer(
        text=text_storage.SUBMISSION_SUCCESSFULLY_SENT.format(
            request_status=RequestStatus.PENDING.label
        ),
        reply_markup=get_go_to_main_menu_keyboard(
            button_text=text_storage.GREAT,
            with_new_message=True,
            with_delete_markup=True,
        ),
        parse_mode=ParseMode.HTML,
    )

    save_request_to_redis(user_mission_submission.id, message.message_id)


@router.message(states.WAITING_FOR_ROBOT_PHOTO)
async def handle_robot_picture_submission(message: Message, state: FSMContext):
    if not message.media_group_id and not message.photo:
        await message.answer(
            text_storage.PHOTO_SUBMISSION_EXPECTED,
            reply_markup=get_cancel_state_keyboard(),
        )
        return

    state_data = await state.get_data()
    mission_id: int | None = state_data.get("mission_id", None)
    await state.clear()

    if not mission_id:
        await message.answer(
            text=text_storage.SOMETHING_WENT_WRONG,
            reply_markup=get_go_to_main_menu_keyboard(
                text_storage.GO_BACK_TO_MAIN_MENU, with_new_message=True
            ),
        )
        return

    ok = await check_old_submissions(
        message, mission_id, MissionVerificationMethod.PHOTO
    )
    if not ok:
        return

    mission = await Mission.objects.get(id=mission_id)

    await UserMissionSubmission.objects.create(
        user_id=message.from_user.id,
        mission_id=mission_id,
        status=RequestStatus.ACCEPTED,
    )
    await check_achievement_updates(message.bot, message.from_user.id)

    file_id = message.photo[-1].file_id

    await resend_submission_photo_util(
        message.bot,
        None,
        file_id,
        chat_id=static.KIDS_ROBOTS_CHAT_ID,
    )

    text = text_storage.NO_VERIFICATION_AND_CHECK_LIST_MISSION_ACCEPTED_INFO.format(
        mission_name=mission.name, mission_score=mission.score
    )

    await message.answer(
        text=text,
        reply_markup=get_go_to_main_menu_keyboard(
            button_text=text_storage.GREAT,
            with_new_message=True,
            with_delete_markup=True,
        ),
        parse_mode=ParseMode.HTML,
    )


@router.message(states.WAITING_FOR_PICTURE_SUBMISSION)
async def handle_picture_submission(message: Message, state: FSMContext):
    if not message.media_group_id and not message.photo:
        await message.answer(
            text_storage.PHOTO_SUBMISSION_EXPECTED,
            reply_markup=get_cancel_state_keyboard(),
        )
        return

    await handle_submission_util(message, state, MissionVerificationMethod.PHOTO)


@router.message(states.WAITING_FOR_VOICE_SUBMISSION)
async def handle_voice_submission(message: Message, state: FSMContext):
    if not message.voice:
        await message.answer(
            text_storage.VOICE_SUBMISSION_EXPECTED,
            reply_markup=get_cancel_state_keyboard(),
        )
        return

    await handle_submission_util(message, state, MissionVerificationMethod.VOICE)


@router.message(states.WAITING_FOR_VIDEO_SUBMISSION)
async def handle_video_submission(message: Message, state: FSMContext):
    if not message.video_note:
        await message.answer(
            text_storage.VIDEO_SUBMISSION_EXPECTED,
            reply_markup=get_cancel_state_keyboard(),
        )
        return

    await handle_submission_util(message, state, MissionVerificationMethod.VIDEO)


@router.message(states.WAITING_FOR_TEXT_SUBMISSION)
async def handle_text_submission(message: Message, state: FSMContext):
    if not message.text or message.text.startswith("/"):
        await message.answer(
            text_storage.TEXT_SUBMISSION_EXPECTED,
            reply_markup=get_cancel_state_keyboard(),
        )
        return

    await handle_submission_util(message, state, MissionVerificationMethod.TEXT)


@router.message(states.WAITING_FOR_VERIFICATION_CODE_SUBMISSION)
async def handle_text_submission(message: Message, state: FSMContext):
    if not message.text or message.text.startswith("/"):
        await message.answer(
            text_storage.TEXT_SUBMISSION_EXPECTED,
            reply_markup=get_cancel_state_keyboard(),
        )
        return

    await handle_submission_util(
        message, state, MissionVerificationMethod.VERIFICATION_CODE
    )


@router.callback_query(RequestAnswerCallbackFactory.filter())
async def handle_request_answer_callback(
    call: CallbackQuery, callback_data: RequestAnswerCallbackFactory
):
    request_id = callback_data.request_id
    is_accepted = callback_data.is_accepted

    user_mission_submission = await UserMissionSubmission.objects.get(id=request_id)
    mission = await Mission.objects.get(id=user_mission_submission.mission_id)

    # todo: check if user submission is already accepted or declined

    status = RequestStatus.ACCEPTED if is_accepted else RequestStatus.DECLINED

    if mission.verification_method == MissionVerificationMethod.VIDEO:
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(
            f"Статус для обращения с кружочком выше: {status.label}"
        )
    elif mission.verification_method in CAPTION_TYPE_VERIFICATION_METHODS:
        text = f"{call.message.caption}\n\nСтатус: {status.label}"
        await call.message.edit_caption(caption=text, reply_markup=None)
        if (
            mission.verification_method == MissionVerificationMethod.PHOTO
            and status == RequestStatus.ACCEPTED
        ):
            # await send_picture_for_rating(call.bot, user_mission_submission.id, call.message.photo[-1].file_id)
            await resend_submission_photo_util(
                call.bot,
                text_storage.RATE_PICTURE_IF_LIKED,
                call.message.photo[-1].file_id,
                chat_id=static.COMMON_PICTURES_CHAT_ID,
                reply_markup=get_picture_rating_keyboard(user_mission_submission.id),
            )
    else:
        text = f"{call.message.text}\n\nСтатус: {status.label}"
        await call.message.edit_text(text=text, reply_markup=None)

    user_mission_submission.status = status
    await user_mission_submission.save()

    kwargs = {
        "chat_id": user_mission_submission.user_id,
        "parse_mode": ParseMode.HTML,
    }

    if message_id := r.get(f"request_{request_id}"):
        kwargs["reply_to_message_id"] = message_id

    if is_accepted:
        user_mission_submission.score = mission.score
        await user_mission_submission.save()

        edit_old_message_new_text = text_storage.SUBMISSION_SUCCESSFULLY_SENT.format(
            request_status=RequestStatus.ACCEPTED.label
        )

        text = text_storage.SUBMISSION_ACCEPTED.format(
            mission_name=mission.name,
            score=mission.score,
        )
        reply_markup = get_go_to_main_menu_keyboard(
            button_text=text_storage.GREAT,
            with_new_message=True,
            with_delete_markup=True,
        )

        await check_achievement_updates(call.bot, user_mission_submission.user_id)

    else:

        edit_old_message_new_text = text_storage.SUBMISSION_SUCCESSFULLY_SENT.format(
            request_status=RequestStatus.DECLINED.label
        )

        if call.from_user.username:

            text = text_storage.SUBMISSION_REJECTED_WITH_MODERATOR.format(
                mission_name=mission.name,
                moderator=f"@{call.from_user.username}",
            )

        else:
            text = text_storage.SUBMISSION_REJECTED.format(
                mission_name=mission.name,
            )

        reply_markup = get_go_to_main_menu_keyboard(
            button_text=text_storage.GOT_IT,
            with_new_message=True,
            with_delete_markup=True,
        )

    if message_id:
        await call.bot.edit_message_text(
            chat_id=user_mission_submission.user_id,
            message_id=message_id,
            text=edit_old_message_new_text,
            reply_markup=None,
            parse_mode=ParseMode.HTML,
        )

    kwargs["text"] = text
    kwargs["reply_markup"] = reply_markup

    await call.bot.send_message(**kwargs)


@router.callback_query(LikePictureCallbackFactory.filter())
async def handle_like_picture_callback(
    call: CallbackQuery, callback_data: LikePictureCallbackFactory
):
    user_mission_submission_id = callback_data.user_mission_submission_id
    user_mission_submission: UserMissionSubmission = (
        await UserMissionSubmission.objects.get(id=user_mission_submission_id)
    )
    user_mission_submission.picture_is_liked = True
    await user_mission_submission.save()

    await check_achievement_updates(call.bot, user_mission_submission.user_id)

    await call.message.edit_caption(
        caption=text_storage.PICTURE_HAS_BEEN_LIKED, reply_markup=None
    )


# Personal progres

@router.callback_query(F.data == ButtonsStorage.MY_PROGRES.callback)
async def handle_my_progres_callback(call: CallbackQuery):
    user_score = await UserMissionSubmission.objects.filter(
        user_id=call.from_user.id, status=RequestStatus.ACCEPTED
    ).all()
    missions_score = sum([submission.mission.score + submission.extra_score for submission in user_score])

    total_users_score = await UserMissionSubmission.objects.filter(
        status=RequestStatus.ACCEPTED
    ).all()
    total_missions_score = sum([submission.mission.score + submission.extra_score for submission in total_users_score])

    await edit_photo_message(
        call.bot,
        call.message,
        photo_url=static.PERSONAL_WORK_MEDIA_URL,
        caption=text_storage.PERSONAL_SCORE_TEXT.format(score=missions_score, team_score=total_missions_score),
        reply_markup=get_back_to_quest_keyboard(),
    )


@router.callback_query(F.data == ButtonsStorage.GO_TO_ACHIEVEMENTS_BUTTON.callback)
async def handle_my_progres_callback(call: CallbackQuery):
    user_achievements = await get_user_achievements(call.from_user.id)

    await edit_photo_message(
        call.bot,
        call.message,
        photo_url=static.MAIN_MENU_MEDIA_URL,
        caption=text_storage.ACHIEVEMENTS_TEXT,
        reply_markup=get_achievements_keyboard(user_achievements),
    )


@router.callback_query(AchievementCallbackFactory.filter())
async def handle_achievement_callback(
    call: CallbackQuery, callback_data: AchievementCallbackFactory
):
    achievement = await Achievement.objects.get(id=callback_data.id)

    user_achievement = await UserAchievement.objects.filter(
        user_id=call.from_user.id, achievement_id=achievement.id
    ).first()

    text = (
        text_storage.ACHIEVEMENT_TEXT
        if not user_achievement
        else text_storage.ACHIEVEMENT_RECEIVED_TEXT
    ).format(
        achievement_name=achievement.name,
        achievement_description=achievement.description,
    )

    await edit_photo_message(
        call.bot,
        message=call.message,
        photo_url=get_achievement_media_url(achievement),
        reply_markup=get_achievement_keyboard(),
        caption=text,
    )


@router.callback_query(F.data == ButtonsStorage.START_TEST_1.callback)
async def handle_start_test_callback(call: CallbackQuery):
    old_test_submission = await UserTest.objects.filter(
        user_id=call.from_user.id
    ).first()

    if old_test_submission:
        await call.answer(
            text=text_storage.TEST_ALREADY_COMPLETED.format(
                score=old_test_submission.score
            ),
            show_alert=True,
        )
        return

    await call.message.delete()
    await call.message.answer(
        text=PRE_TEST_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=get_pretest_keyboard()
    )


@router.callback_query(F.data == ButtonsStorage.START_TEST_2.callback)
async def handle_start_test_callback(call: CallbackQuery):
    old_test_submission = await UserTest.objects.filter(
        user_id=call.from_user.id
    ).first()

    if old_test_submission:
        await call.answer(
            text=text_storage.TEST_ALREADY_COMPLETED.format(
                score=old_test_submission
            ),
            show_alert=True,
        )
        return

    await call.message.delete()
    await call.message.answer(
        text=text_storage.QUESTION_1,
        reply_markup=get_first_question_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data.in_(static.TEST_Q_1_BUTTONS))
async def handle_first_question_answer(call: CallbackQuery):
    if call.data == ButtonsStorage.OPTION_1_2.callback:
        r.set(f"test_{call.from_user.id}_1", "True")
    else:
        r.set(f"test_{call.from_user.id}_1", "False")

    await call.message.edit_text(
        text=text_storage.QUESTION_2,
        reply_markup=get_second_question_keyboard(),
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data.in_(static.TEST_Q_2_BUTTONS))
async def handle_second_question_answer(call: CallbackQuery):
    if call.data == ButtonsStorage.OPTION_2_1.callback:
        r.set(f"test_{call.from_user.id}_2", "True")
    else:
        r.set(f"test_{call.from_user.id}_2", "False")

    await call.message.edit_text(
        text=text_storage.QUESTION_3,
        reply_markup=get_third_question_keyboard(),
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data.in_(static.TEST_Q_3_BUTTONS))
async def handle_third_question_answer(call: CallbackQuery):
    if call.data == ButtonsStorage.OPTION_3_2.callback:
        r.set(f"test_{call.from_user.id}_3", "True")
    else:
        r.set(f"test_{call.from_user.id}_3", "False")

    await call.message.edit_text(
        text=text_storage.QUESTION_4,
        reply_markup=get_fourth_question_keyboard(),
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data.in_(static.TEST_Q_4_BUTTONS))
async def handle_third_question_answer(call: CallbackQuery):
    if call.data == ButtonsStorage.OPTION_4_4.callback:
        r.set(f"test_{call.from_user.id}_4", "True")
    else:
        r.set(f"test_{call.from_user.id}_4", "False")

    await call.message.edit_text(
        text=text_storage.QUESTION_5,
        reply_markup=get_fifth_question_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data.in_(static.TEST_Q_5_BUTTONS))
async def handle_third_question_answer(call: CallbackQuery):
    if call.data == ButtonsStorage.OPTION_5_3.callback:
        r.set(f"test_{call.from_user.id}_5", "True")
    else:
        r.set(f"test_{call.from_user.id}_5", "False")

    cnt = 0
    for i in range(1, 6):
        if r.get(f"test_{call.from_user.id}_{i}") == 'True':
            cnt += 1

    await UserTest.objects.get_or_create(
        user_id=call.from_user.id,
        score=cnt
    )

    score_string = get_score_name(cnt)
    score = f"{cnt} {score_string}"
    text = f'Твой результат: {score}\n\n'
    if cnt < 4:
        extra_text = "К сожалению, ты не набрал нужное количество баллов.\nНе расстраивайся! Если хочешь узнавать больше об экологичных привычках, подписывайся на наш канал!"
    else:
        extra_text = "Поздравляем! Ты набрал нужное количество баллов. Подойди на ресепшен и <b>получи свой подарок</b>\n\nА если хочешь узнавать больше об экологичных привычках, подписывайся на наш канал!"
    text = text + extra_text
    await call.message.edit_text(
        text=text,
        reply_markup=get_after_test_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await send_photo_message(
        call.message.bot,
        call.message.chat.id,
        photo_url=static.MAIN_MENU_MEDIA_URL,
        caption=text_storage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(call.from_user.id),
    )


@router.message(states.WAITING_FOR_ADMIN_MESSAGE)
async def handle_robot_picture_submission(message: Message, state: FSMContext):

    await state.clear()

    if message.from_user.id not in static.ADMIN_IDS:
        await message.answer(
            text="У вас нет прав на отправку сообщений в этот чат."
        )
        return

    await message.answer(
        text="Отправляю.."
    )

    users = await User.objects.all()

    if not message.media_group_id and not message.photo:
        for user in users:
            try:
                await message.bot.send_message(
                    chat_id=user.id,
                    text=message.text,
                    reply_markup=get_one_button_keyboard(ButtonsStorage.HIDE_MESSAGE)
                )
            except Exception:
                pass

    else:

        file_id = message.photo[-1].file_id

        for user in users:
            try:
                await message.bot.send_photo(
                    chat_id=user.id,
                    photo=file_id,
                    caption=message.caption,
                    reply_markup=get_one_button_keyboard(ButtonsStorage.HIDE_MESSAGE)
                )
            except Exception:
                pass

    await message.answer("Сообщение отправлено всем пользователям.")
