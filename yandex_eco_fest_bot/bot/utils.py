from aiogram import Bot
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, FSInputFile

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
from yandex_eco_fest_bot.bot.tools.keyboards.keyboards import (
    get_locations_menu_keyboard, )
from yandex_eco_fest_bot.core import config
from yandex_eco_fest_bot.core.redis_config import r
from yandex_eco_fest_bot.db.tables import (
    Location,
    Mission,
    UserMissionSubmission,
    Achievement,
    UserAchievement,
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
    return f"<b>{location.name}</b>" f"{location.description}"
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
