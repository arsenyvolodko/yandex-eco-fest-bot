from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.types.input_media_photo import InputMediaPhoto

from yandex_eco_fest_bot.bot import text_storage, static
from yandex_eco_fest_bot.bot.enums import RequestStatus
from yandex_eco_fest_bot.bot.enums.mission_verification_method import (
    MissionVerificationMethod,
)
from yandex_eco_fest_bot.bot.schemas import AchievementStatus
from yandex_eco_fest_bot.bot.schemas.missions_display_schema import (
    MissionStatus,
    LocationMissionsStatus,
)
from yandex_eco_fest_bot.bot.static import VERIFICATION_METHOD_TO_STATE
from yandex_eco_fest_bot.bot.tools.keyboards import button_storage
from yandex_eco_fest_bot.bot.tools.keyboards.button_storage import ButtonsStorage
from yandex_eco_fest_bot.bot.tools.keyboards.keyboards import (
    get_locations_menu_keyboard, get_one_button_keyboard, get_go_to_main_menu_keyboard, )
from yandex_eco_fest_bot.core import config
from yandex_eco_fest_bot.core.redis_config import r
from yandex_eco_fest_bot.db.tables import (
    Location,
    Mission,
    UserMissionSubmission,
    Achievement,
    UserAchievement, User,
)


async def edit_photo_message(
    bot: Bot, message: Message, photo_url: str, caption: str, **kwargs
):
    file_id = r.get(photo_url)
    file_id = None
    media = file_id or photo_url

    if media == static.MAIN_MENU_MEDIA_URL:
        media = FSInputFile(f"{config.LOCAL_MEDIA_DIR}/main.png")

    msg = await bot.edit_message_media(
        media=InputMediaPhoto(media=media, caption=caption, parse_mode=ParseMode.HTML),
        chat_id=message.chat.id,
        message_id=message.message_id,
        **kwargs,
    )

    if not file_id:
        r.set(photo_url, value=msg.photo[-1].file_id)


async def send_photo_message(
    bot: Bot, chat_id: int, photo_url: str, caption: str, **kwargs
):
    file_id = r.get(photo_url)
    # file_id = None
    photo = file_id or photo_url

    if photo == static.MAIN_MENU_MEDIA_URL:
        photo = FSInputFile(f"{config.LOCAL_MEDIA_DIR}/main.png")

    msg = await bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=caption,
        parse_mode=ParseMode.HTML,
        **kwargs,
    )

    if not file_id:
        r.set(photo_url, value=msg.photo[-1].file_id)


def get_location_media_url(location: Location):
    print(f"{static.LOCATIONS_MEDIA_DIR}/{location.id}.png")
    return f"{static.LOCATIONS_MEDIA_DIR}/{location.id}.png"


def get_achievement_media_url(achievement: Achievement):
    return f"{static.ACHIEVEMENTS_MEDIA_DIR}/{achievement.id}.png"


async def send_start_achievement(bot, chat_id, achievement: Achievement):
    media_url = get_achievement_media_url(achievement)
    text = text_storage.GET_ACHIEVEMENTS_TEXT.format(achievement_name=achievement.name)
    text += f"\n\n{text_storage.EXTRA_INTRO_ACHIEVEMENT_TEXT}"

    await send_photo_message(
        bot=bot,
        chat_id=chat_id,
        photo_url=media_url,
        caption=text,
        reply_markup=get_go_to_main_menu_keyboard(
            button_text="Отлично!",
            with_new_message=True,
            with_delete_markup=True,
        )
    )


async def send_locations_with_image(call: CallbackQuery, locations: list[Location]):
    locations_file_id = r.get("LOCATIONS_MAP_FILE_ID")

    if not locations_file_id:
        photo = FSInputFile(config.MEDIA_DIR / "locations_map.png")
        msg = await call.bot.send_photo(
            chat_id=call.message.chat.id,
            photo=photo,
            caption=text_storage.LOCATIONS_MAP_TEXT,
            reply_markup=get_locations_menu_keyboard(locations),
        )
        r.set("LOCATIONS_MAP_FILE_ID", value=msg.photo[-1].file_id)
        return

    await call.bot.send_photo(
        call.message.chat.id,
        locations_file_id,
        caption=text_storage.LOCATIONS_MAP_TEXT,
        reply_markup=get_locations_menu_keyboard(locations),
    )


async def resend_submission_photo_util(
    bot: Bot, text: str | None, file_id: str, **kwargs
):
    await bot.send_photo(
        photo=file_id,
        caption=text,
        **kwargs,
    )


async def resend_submission_text_util(bot: Bot, text: str, resend_kwargs: dict):
    await bot.send_message(
        text=text,
        **resend_kwargs,
    )


async def resend_submission_voice_util(
    bot: Bot, text: str, file_id: str, resend_kwargs: dict
):
    await bot.send_voice(
        voice=file_id,
        caption=text,
        **resend_kwargs,
    )


async def get_missions_with_score(
    user_id: int, location: Location
) -> LocationMissionsStatus:
    user_submissions: list[UserMissionSubmission] = (
        await UserMissionSubmission.objects.filter(user_id=user_id).all()
    )

    accepted_missions: set[Mission] = set()
    rejected_missions: set[Mission] = set()
    in_progress_missions: set[Mission] = set()

    missions = set(location.missions)

    for submission in user_submissions:
        if submission.mission.location != location:
            continue
        if submission.status == RequestStatus.ACCEPTED:
            accepted_missions.add(submission.mission)
        elif submission.status == RequestStatus.PENDING:
            in_progress_missions.add(submission.mission)
        elif submission.status == RequestStatus.DECLINED:
            rejected_missions.add(submission.mission)

    res_missions: list[MissionStatus] = []
    for mission in missions:
        kwargs = {
            "mission": mission,
        }

        if mission in accepted_missions:
            res_missions.append(MissionStatus(status=RequestStatus.ACCEPTED, **kwargs))

        elif mission in in_progress_missions:
            res_missions.append(MissionStatus(status=RequestStatus.PENDING, **kwargs))

        elif mission in rejected_missions:
            res_missions.append(MissionStatus(status=RequestStatus.DECLINED, **kwargs))

        else:
            res_missions.append(MissionStatus(status=None, **kwargs))

    res_missions.sort(key=lambda x: x.mission.order)

    return LocationMissionsStatus(location=location, missions=res_missions)


def save_request_to_redis(request_id: int, message_id: int):
    r.set(f"request_{request_id}", message_id)


def get_location_info_text(location: Location) -> str:
    return f"<b>{location.name}</b>\n\n{location.description}"
#
#
# def get_mission_info_text(
#     mission: Mission, old_submission: UserMissionSubmission | None
# ) -> str:
#     if not old_submission:
#         return f"<b>{mission.name}</b>\n\n" f"{mission.description}"
#
#     status = old_submission.status
#
#     if status == RequestStatus.ACCEPTED:
#         text = text_storage.MISSION_ACCEPTED_INFO
#         if mission.verification_method == MissionVerificationMethod.VERIFICATION_CODE:
#             text = text_storage.VERIFICATION_CODE_ACCEPTED_INFO
#         elif (
#             mission.verification_method == MissionVerificationMethod.NO_VERIFICATION
#             or mission.verification_method == MissionVerificationMethod.CHECK_LIST
#         ):
#             text = text_storage.NO_VERIFICATION_AND_CHECK_LIST_MISSION_ACCEPTED_INFO
#
#         return text.format(
#             mission_name=mission.name,
#             mission_score=mission.score + old_submission.extra_score,
#             mission_description=mission.description,
#         )
#
#     if status == RequestStatus.DECLINED:
#         text = text_storage.MISSION_DECLINED_INFO
#         if mission.verification_method == MissionVerificationMethod.VERIFICATION_CODE:
#             text = text_storage.VERIFICATION_CODE_SUBMISSION_REJECTED
#
#         return text.format(
#             mission_name=mission.name,
#             mission_description=mission.description,
#         )
#
#     if status == RequestStatus.PENDING:
#         return text_storage.MISSION_PENDING_INFO.format(
#             mission_name=mission.name,
#             mission_description=mission.description,
#         )


async def get_user_achievements(user_id: int) -> list[AchievementStatus]:
    achievements = await Achievement.objects.all()
    user_achievements = await UserAchievement.objects.filter(user_id=user_id).all()

    user_achievements_set = set(
        [user_achievement.achievement for user_achievement in user_achievements]
    )

    res_achievements: list[AchievementStatus] = [
        AchievementStatus(
            achievement=achievement,
            is_succeeded=True if achievement in user_achievements_set else False,
        )
        for achievement in achievements
    ]

    return res_achievements


def get_state_by_verification_method(
    verification_method: MissionVerificationMethod,
) -> State:
    return VERIFICATION_METHOD_TO_STATE[verification_method]


def check_verification_code(mission: Mission, message_text: str):
    expected_text = mission.verification_message.strip().lower()
    return expected_text == message_text.strip().lower()


async def process_verification_code_submission(
    mission: Mission, user_id: int, success: bool
) -> str:
    if success:
        await UserMissionSubmission.objects.create(
            user_id=user_id,
            mission_id=mission.id,
            status=RequestStatus.ACCEPTED,
        )
        return text_storage.NO_VERIFICATION_AND_CHECK_LIST_MISSION_ACCEPTED_INFO.format(
            mission_name=mission.name,
            mission_score=mission.score,
        )
    else:
        await UserMissionSubmission.objects.create(
            user_id=user_id,
            mission_id=mission.id,
            status=RequestStatus.DECLINED,
        )
        return text_storage.VERIFICATION_CODE_SUBMISSION_REJECTED


async def get_mission_task_text(
    mission: Mission, old_submission: UserMissionSubmission | None
) -> str:
    text = f"<b>{mission.name}</b>\n\n"

    if old_submission:
        text += f"Статус прохождения эко-миссии: <b>{old_submission.status.label}</b>\n\n"
        if old_submission.status == RequestStatus.ACCEPTED:
            text += (f"<b>Вы набрали {mission.score + old_submission.extra_score} 🌱кредитов за выполнение эко-миссии.</b>\n"
                     f"Вы не можете пройти ее повторно.\n\n")
        else:
            if old_submission.status == RequestStatus.DECLINED:
                text += "Вы можете попробовать выполнить задание еще раз.\n"

    if not old_submission or old_submission.status != RequestStatus.ACCEPTED:
        if mission.verification_method == MissionVerificationMethod.CHECK_LIST:
            mission_max_score = len(static.CHECK_LIST_QUESTIONS) * static.CHECK_LIST_POINT_SCORE
        else:
            mission_max_score = mission.score

        text += f"Максимальное количество 🌱кредитов за выполнение задания - {mission_max_score}\n\n"

    text += "Твое задание в рамках эко-миссии:\n"
    text += f"{mission.description}\n\n"

    if mission.verification_method in static.VERIFICATION_METHOD_TEXT and (not old_submission or old_submission.status == RequestStatus.DECLINED):
        text += f"{static.VERIFICATION_METHOD_TEXT[mission.verification_method]}\n\n"

    if mission.extra_text and (not old_submission or old_submission.status == RequestStatus.DECLINED):
        text += f"{mission.extra_text}"

    return text


# Achievements related functions


async def get_user_missions_score(user_id: int) -> int:
    user_submissions = await UserMissionSubmission.objects.filter(user_id=user_id, status=RequestStatus.ACCEPTED).all()
    score = 0

    for submission in user_submissions:
        # if submission.status == RequestStatus.ACCEPTED:
        score += submission.mission.score + submission.extra_score

    return score


async def check_credits_achievements(user_id: int, user_score: int):
    scores = [50, 100, 500]

    for ind, score in enumerate(scores, start=1):
        if user_score >= score:
            await UserAchievement.objects.get_or_create(
                user_id=user_id, achievement_id=ind
            )


async def check_any_mission_achievement(user_id: int, accepted_submissions: list[UserMissionSubmission]):
    location_ids = set()
    for submission in accepted_submissions:
        location_ids.add(submission.mission.location_id)

    location_ids -= {static.ROBOLAB_KIDS_LOCATION_ID}

    if len(location_ids) == static.LOCATIONS_TOTAL_COUNT:
        await UserAchievement.objects.get_or_create(
            user_id=user_id, achievement_id=static.ANY_MISSION_FROM_ALL_LOCATIONS_ACHIEVEMENT_ID
        )


async def check_fix_it_pro_achievement(user_id: int, accepted_submissions: list[UserMissionSubmission]):
    mission_ids = {submission.mission_id for submission in accepted_submissions}

    if static.REPAIR_CAFE_MISSION_ID in mission_ids and static.UPCYCLING_MISSION_ID in mission_ids:
        await UserAchievement.objects.get_or_create(
            user_id=user_id, achievement_id=static.FIX_IT_PRO_ACHIEVEMENT_ID
        )


async def check_achievement_updates(user_id: int):
    user = User.objects.get(id=user_id)

    accepted_submissions = await UserMissionSubmission.objects.filter(
        user_id=user_id, status=RequestStatus.ACCEPTED
    ).all()

    user_score = await get_user_missions_score(user_id)

    # «Зелёный старт» 🚀, «Сила сотни» 💯, «Eco Legend» 🏆 (1-3)
    await check_credits_achievements(user_id, user_score)

    # «Тур по зонам» 🗺 (4 - ANY_MISSION_FROM_ALL_LOCATIONS_ACHIEVEMENT_ID)
    await check_any_mission_achievement(user_id, accepted_submissions)

    # recycler ??

    # «Fix-It Pro» 🔧 (6 - FIX_IT_PRO_ACHIEVEMENT_ID, REPAIR_CAFE_MISSION_ID, UPCYCLING_MISSION_ID)



