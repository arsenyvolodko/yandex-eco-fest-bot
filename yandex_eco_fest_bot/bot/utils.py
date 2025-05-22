from collections import defaultdict

from aiogram.enums import ParseMode
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, FSInputFile, User

from yandex_eco_fest_bot.bot import text_storage
from yandex_eco_fest_bot.bot.enums import RequestStatus
from yandex_eco_fest_bot.bot.enums.mission_verification_method import (
    MissionVerificationMethod,
)
from yandex_eco_fest_bot.bot.schemas import AchievementStatus
from yandex_eco_fest_bot.bot.schemas.missions_display_schema import (
    MissionStatus,
    LocationMissionsStatus,
)
from yandex_eco_fest_bot.bot.tools import states
from yandex_eco_fest_bot.bot.tools.keyboards.keyboards import (
    get_locations_menu_keyboard,
    get_submission_options_keyboard,
)
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


async def resend_submission(
    bot,
    mission: Mission,
    user: User,
    file_id: str | None = None,
    text: str | None = None,
) -> UserMissionSubmission:
    location = await Location.objects.get(id=mission.location_id)

    user_mission_submission = await UserMissionSubmission.objects.create(
        user_id=user.id,
        mission_id=mission.id,
    )

    text = text_storage.SUBMISSION_REQUEST_TEXT.format(
        username=user.username,
        mission_name=mission.name,
    )

    kwargs = {
        "chat_id": location.chat_id,
        "reply_markup": get_submission_options_keyboard(user_mission_submission.id),
        "parse_mode": ParseMode.HTML,
    }

    if not file_id:
        await bot.send_message(
            text=text,
            **kwargs,
        )
        return user_mission_submission

    await bot.send_photo(
        photo=file_id,
        caption=text,
        **kwargs,
    )

    return user_mission_submission


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


def get_mission_info_text(mission: Mission, status: RequestStatus | None) -> str:
    if not status:
        return f"<b>{mission.name}</b>\n\n" f"{mission.description}"
    if status == RequestStatus.ACCEPTED:
        return text_storage.MISSION_ACCEPTED_INFO.format(
            mission_name=mission.name,
            mission_score=mission.score,
            mission_description=mission.description,
        )
    if status == RequestStatus.DECLINED:
        return text_storage.MISSION_DECLINED_INFO.format(
            mission_name=mission.name,
            mission_description=mission.description,
        )
    if status == RequestStatus.PENDING:
        return text_storage.MISSION_PENDING_INFO.format(
            mission_name=mission.name,
            mission_description=mission.description,
        )


async def get_user_achievements(user_id: int) -> list[AchievementStatus]:
    achievements = await Achievement.objects.all()
    user_achievements = await UserAchievement.objects.filter(user_id=user_id).all()

    user_achievements_set = set([user_achievement.achievement for user_achievement in user_achievements])
    print(achievements)
    print(user_achievements_set)

    res_achievements: list[AchievementStatus] = [
        AchievementStatus(
            achievement=achievement,
            is_succeeded=True if achievement in user_achievements_set else False,
        )
        for achievement in achievements
    ]
    # res_achievements = []
    #
    # for achievement in achievements:
    #     print("cur:", achievement)
    #     is_succeeded = False
    #     if achievement in user_achievements_set:
    #         print("in")
    #         is_succeeded = True
    #     res_achievements.append(
    #         AchievementStatus(
    #             achievement=achievement,
    #             is_succeeded=is_succeeded
    #         )
    #     )
    #
    # print(res_achievements)

    return res_achievements


VERIFICATION_METHOD_TO_STATE = {
    MissionVerificationMethod.PHOTO: states.WAITING_FOR_PICTURE_SUBMISSION,
    MissionVerificationMethod.TEXT: states.WAITING_FOR_TEXT_SUBMISSION,
}


def get_state_by_verification_method(
    verification_method: MissionVerificationMethod,
) -> State:
    return VERIFICATION_METHOD_TO_STATE[verification_method]
