import logging

from aiogram import Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from yandex_eco_fest_bot.bot import text_storage
from yandex_eco_fest_bot.bot.enums import RequestStatus, MissionVerificationMethod
from yandex_eco_fest_bot.bot.schemas import LocationMissionsStatus
from yandex_eco_fest_bot.bot.tools import states
from yandex_eco_fest_bot.bot.tools.factories import (
    LocationPageCallbackFactory,
    MainMenuCallbackFactory,
    LocationCallbackFactory,
    MissionCallbackFactory,
    RequestAnswerCallbackFactory,
    AchievementCallbackFactory,
    AchievementPageCallbackFactory,
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
    get_achievements_keyboard,
    get_achievement_keyboard,
    get_go_to_achievements_keyboard,
)
from yandex_eco_fest_bot.bot.utils import (
    send_locations_with_image,
    get_location_info_text,
    get_mission_info_text,
    get_state_by_verification_method,
    VERIFICATION_METHOD_TO_STATE,
    resend_submission,
    save_request_to_redis,
    get_missions_with_score,
    get_user_achievements,
)
from yandex_eco_fest_bot.core.redis_config import r
from yandex_eco_fest_bot.db.tables import (
    User,
    Location,
    Mission,
    UserMissionSubmission,
    Achievement,
    UserAchievement,
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
    )


@router.callback_query(F.data == ButtonsStorage.AFTER_START_BUTTON.callback)
async def handle_after_start_callback(call: CallbackQuery):
    await call.message.edit_text(
        text_storage.AFTER_START_TEXT.format(name=call.from_user.first_name),
        reply_markup=get_go_to_main_menu_keyboard(button_text="Поехали!"),
    )


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


# Locations


@router.callback_query(F.data == ButtonsStorage.LOCATIONS_MAP.callback)
async def handle_location_map_callback(call: CallbackQuery):
    await call.message.delete()
    locations = await Location.objects.filter(parent=None).all()
    await send_locations_with_image(call, locations)


@router.callback_query(LocationPageCallbackFactory.filter())
async def handle_location_page_callback(
    call: CallbackQuery, callback_data: LocationPageCallbackFactory
):
    locations = await Location.objects.filter(parent=None).all()
    await call.message.edit_reply_markup(
        reply_markup=get_locations_menu_keyboard(
            locations, page_number=callback_data.page
        )
    )


@router.callback_query(LocationCallbackFactory.filter())
async def handle_location_callback(
    call: CallbackQuery, callback_data: LocationCallbackFactory, state: FSMContext
):
    await state.clear()

    location = await Location.objects.get(id=callback_data.id)
    text = get_location_info_text(location)

    if location.is_group:
        locations = await Location.objects.filter(parent=location).all()
        reply_markup = get_locations_menu_keyboard(
            locations, back_to_locations_parent=location
        )
    else:

        missions_status_score_schema: LocationMissionsStatus = (
            await get_missions_with_score(user_id=call.from_user.id, location=location)
        )
        reply_markup = get_missions_keyboard(missions_status_score_schema)

    kwargs = {"text": text, "reply_markup": reply_markup, "parse_mode": ParseMode.HTML}

    if not callback_data.with_new_message:
        await call.message.edit_text(**kwargs)
        return

    await call.message.delete()
    await call.message.answer(**kwargs)


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

    text = get_mission_info_text(mission, status)

    if not old_submission or old_submission.status == RequestStatus.DECLINED:

        verification_method = mission.verification_method
        if verification_method in VERIFICATION_METHOD_TO_STATE:
            new_state = get_state_by_verification_method(mission.verification_method)

            await state.set_state(new_state)
            await state.update_data(
                {
                    "mission_id": mission.id,
                    "msg_id": call.message.message_id,
                }
            )

        await call.message.edit_text(
            text=text,
            reply_markup=get_specific_mission_keyboard(mission),
            parse_mode=ParseMode.HTML,
        )

        return

    await call.message.edit_text(
        text=text,
        reply_markup=get_specific_mission_keyboard(mission),
        parse_mode=ParseMode.HTML,
    )


@router.message(states.WAITING_FOR_PICTURE_SUBMISSION)
async def handle_picture_submission(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer(
            text_storage.PHOTO_SUBMISSION_EXPECTED,
            reply_markup=get_cancel_state_keyboard(),
        )
        return

    state_data = await state.get_data()
    await state.clear()

    mission_id = state_data.get("mission_id")
    msg_id = state_data.get("msg_id")

    if not mission_id:
        await message.answer(
            text=text_storage.SOMETHING_WENT_WRONG,
            reply_markup=get_go_to_main_menu_keyboard(
                text_storage.GO_BACK_TO_MAIN_MENU
            ),
        )
        return

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

            return

        elif old_submission.status == RequestStatus.PENDING:
            await message.answer(
                text=text_storage.MISSION_IN_PROGRESS_ALERT,
                reply_markup=get_go_to_main_menu_keyboard(
                    text_storage.GO_BACK_TO_MAIN_MENU,
                    with_new_message=True,
                    with_delete_markup=True,
                ),
            )

            return

        await old_submission.delete()

    file_id = message.photo[-1].file_id
    user_submission = await resend_submission(
        message.bot, mission, message.from_user, file_id=file_id
    )

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

    save_request_to_redis(user_submission.id, message.message_id)


@router.callback_query(RequestAnswerCallbackFactory.filter())
async def handle_request_answer_callback(
    call: CallbackQuery, callback_data: RequestAnswerCallbackFactory
):
    request_id = callback_data.request_id
    is_accepted = callback_data.is_accepted

    user_mission_submission = await UserMissionSubmission.objects.get(id=request_id)
    mission = await Mission.objects.get(id=user_mission_submission.mission_id)

    status = RequestStatus.ACCEPTED if is_accepted else RequestStatus.DECLINED

    if mission.verification_method == MissionVerificationMethod.PHOTO:
        text = f"{call.message.caption}\n\nСтатус: {status.label}"
        await call.message.edit_caption(caption=text, reply_markup=None)
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

    else:

        edit_old_message_new_text = text_storage.SUBMISSION_SUCCESSFULLY_SENT.format(
            request_status=RequestStatus.DECLINED.label
        )

        text = text_storage.SUBMISSION_REJECTED.format(
            mission_name=mission.name,
            moderator=f"@{call.from_user.username}",
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


# Personal progres


@router.callback_query(F.data == ButtonsStorage.MY_PROGRES.callback)
async def handle_my_progres_callback(call: CallbackQuery):
    user_score = await UserMissionSubmission.objects.filter(
        user_id=call.from_user.id, status=RequestStatus.ACCEPTED
    ).all()
    missions_score = sum([submission.mission.score for submission in user_score])

    await call.message.edit_text(
        text=text_storage.PERSONAL_SCORE_TEXT.format(score=missions_score),
        reply_markup=get_go_to_achievements_keyboard(),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == ButtonsStorage.GO_TO_ACHIEVEMENTS_BUTTON.callback)
async def handle_my_progres_callback(call: CallbackQuery):

    user_achievements = await get_user_achievements(call.from_user.id)

    await call.message.edit_text(
        text=text_storage.ACHIEVEMENTS_TEXT,
        reply_markup=get_achievements_keyboard(user_achievements),
        parse_mode=ParseMode.HTML,
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
    )

    await call.message.edit_text(
        text=text.format(
            achievement_name=achievement.name,
            achievement_description=achievement.description,
        ),
        reply_markup=get_achievement_keyboard(achievement),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(AchievementPageCallbackFactory.filter())
async def handle_achievement_page_callback(
    call: CallbackQuery, callback_data: AchievementPageCallbackFactory
):
    user_score = await UserMissionSubmission.objects.filter(
        user_id=call.from_user.id, status=RequestStatus.ACCEPTED
    ).all()
    missions_score = sum([submission.mission.score for submission in user_score])

    user_achievements = await get_user_achievements(call.from_user.id)
    await call.message.edit_text(
        text=text_storage.ACHIEVEMENTS_TEXT.format(score=missions_score),
        reply_markup=get_achievements_keyboard(
            user_achievements, page_num=callback_data.page
        ),
        parse_mode=ParseMode.HTML,
    )


# Team Score


@router.callback_query(F.data == ButtonsStorage.TEAM_PROGRES.callback)
async def handle_my_progres_callback(call: CallbackQuery):
    user_score = await UserMissionSubmission.objects.filter(
        status=RequestStatus.ACCEPTED
    ).all()
    missions_score = sum([submission.mission.score for submission in user_score])
    await call.message.edit_text(
        text=text_storage.TEAM_SCORE_TEXT.format(score=missions_score),
        reply_markup=get_go_to_main_menu_keyboard(
            button_text=text_storage.GO_BACK_TO_MAIN_MENU
        ),
        parse_mode=ParseMode.HTML,
    )
