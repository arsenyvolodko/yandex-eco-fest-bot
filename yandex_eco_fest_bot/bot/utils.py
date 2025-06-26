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

    try:
        msg = await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            parse_mode=ParseMode.HTML,
            **kwargs,
        )
        if not file_id:
            r.set(photo_url, value=msg.photo[-1].file_id)
    except Exception as e:
        try:
            msg = await bot.send_photo(
                chat_id=chat_id,
                photo=photo_url,
                caption=caption,
                parse_mode=ParseMode.HTML,
                **kwargs,
            )
            if not file_id:
                r.set(photo_url, value=msg.photo[-1].file_id)
        except Exception as e:
            pass


def get_location_media_url(location: Location):
    print(f"{static.LOCATIONS_MEDIA_DIR}/{location.id}.png")
    return f"{static.LOCATIONS_MEDIA_DIR}/{location.id}.png"


def get_achievement_media_url(achievement: Achievement):
    return f"{static.ACHIEVEMENTS_MEDIA_DIR}/{achievement.id}.png"


def get_score_name(score: int) -> str:
    str_score = str(score)
    if str_score[-1] == '1':
        return "балл"
    elif str_score[-1] in ('2', '3', '4'):
        return "балла"
    else:
        return "баллов"


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


async def send_achievement(bot, chat_id, achievement: Achievement):
    media_url = get_achievement_media_url(achievement)
    text = text_storage.GET_ACHIEVEMENTS_TEXT.format(achievement_name=achievement.name)

    await send_photo_message(
        bot=bot,
        chat_id=chat_id,
        photo_url=media_url,
        caption=text,
        reply_markup=get_one_button_keyboard(
            ButtonsStorage.HIDE_MESSAGE
        )
    )


async def get_user_missions_score(user_id: int) -> int:
    user_submissions = await UserMissionSubmission.objects.filter(user_id=user_id, status=RequestStatus.ACCEPTED).all()
    score = 0

    for submission in user_submissions:
        score += submission.mission.score + submission.extra_score

    return score


async def check_credits_achievements(bot, user_id: int, user_score: int):
    scores = [50, 100, 500]

    for ind, score in enumerate(scores, start=2):
        if user_score >= score:
            user_achievement, created = await UserAchievement.objects.get_or_create(
                user_id=user_id, achievement_id=ind
            )
            achievement = await Achievement.objects.get(id=ind)
            if created:
                await send_achievement(
                    bot, user_id, achievement
                )


async def check_any_mission_achievement(bot, user_id: int, accepted_submissions: list[UserMissionSubmission], achievement_id: int):
    location_ids = {submission.mission.location_id for submission in accepted_submissions}
    location_ids -= {static.ROBOLAB_KIDS_LOCATION_ID}

    LOCATIONS_TOTAL_COUNT_WITH_MISSIONS = 12

    print(f"Location IDs: {location_ids}, Total Count: {LOCATIONS_TOTAL_COUNT_WITH_MISSIONS}")
    if len(location_ids) == LOCATIONS_TOTAL_COUNT_WITH_MISSIONS - 1:
        user_achievement, created = await UserAchievement.objects.get_or_create(
            user_id=user_id, achievement_id=achievement_id
        )
        if created:
            achievement = await Achievement.objects.get(id=achievement_id)
            await send_achievement(bot, user_id, achievement)


async def check_recycler_achievement(bot, user_id: int, accepted_submissions: list[UserMissionSubmission], achievement_id):
    RECYCLER_MISSION_ID = 4
    mission_ids = {submission.mission_id for submission in accepted_submissions}
    if RECYCLER_MISSION_ID in mission_ids:
        user_achievement, created = await UserAchievement.objects.get_or_create(
            user_id=user_id, achievement_id=achievement_id
        )
        if created:
            achievement = await Achievement.objects.get(id=achievement_id)
            await send_achievement(bot, user_id, achievement)


async def check_fix_it_pro_achievement(bot, user_id: int, accepted_submissions: list[UserMissionSubmission], achievement_id):
    mission_ids = {submission.mission_id for submission in accepted_submissions}

    UPCYCLE_ACHIEVEMENT_ID = 10
    REPAIR_CAFE_MISSION_ID = 12

    if REPAIR_CAFE_MISSION_ID in mission_ids and UPCYCLE_ACHIEVEMENT_ID in mission_ids:
        user_achievement, created = await UserAchievement.objects.get_or_create(
            user_id=user_id, achievement_id=achievement_id
        )
        if created:
            achievement = await Achievement.objects.get(id=achievement_id)
            await send_achievement(bot, user_id, achievement)


async def check_digital_detoxer_achievement(bot, user_id: int, accepted_submissions: list[UserMissionSubmission], achievement_id: int):
    mission_ids = {submission.mission_id for submission in accepted_submissions}

    CHECK_LIST_MISSION_ID = 6
    if CHECK_LIST_MISSION_ID in mission_ids:
        user_mission_submission = await UserMissionSubmission.objects.get(
            user_id=user_id, mission_id=CHECK_LIST_MISSION_ID
        )
        if user_mission_submission.extra_score >= static.CHECK_LIST_POINT_SCORE * 8:
            user_achievement, created = await UserAchievement.objects.get_or_create(
                user_id=user_id, achievement_id=achievement_id
            )
            if created:
                achievement = await Achievement.objects.get(id=achievement_id)
                await send_achievement(bot, user_id, achievement)


async def check_photo_achievement(bot, user_id: int, accepted_submissions: list[UserMissionSubmission], achievement_id: int):
    liked_cnt = 0
    for submission in accepted_submissions:
        if submission.picture_is_liked:
            liked_cnt += 1
    if liked_cnt >= 3:
        user_achievement, created = await UserAchievement.objects.get_or_create(
            user_id=user_id, achievement_id=achievement_id
        )
        if created:
            achievement = await Achievement.objects.get(id=achievement_id)
            await send_achievement(bot, user_id, achievement)


async def check_swap_star_achievement(bot, user_id: int, accepted_submissions: list[UserMissionSubmission], achievement_id: int):
    TECH_SWAP_MISSION_ID = 3
    ECO_SWAP_MISSION_ID = 4

    mission_ids = {submission.mission_id for submission in accepted_submissions}
    if TECH_SWAP_MISSION_ID in mission_ids and ECO_SWAP_MISSION_ID in mission_ids:
        user_achievement, created = await UserAchievement.objects.get_or_create(
            user_id=user_id, achievement_id=achievement_id
        )
        if created:
            achievement = await Achievement.objects.get(id=achievement_id)
            await send_achievement(bot, user_id, achievement)


async def check_achievement_updates(bot, user_id: int):
    # user = await User.objects.get(id=user_id)

    accepted_submissions = await UserMissionSubmission.objects.filter(
        user_id=user_id, status=RequestStatus.ACCEPTED
    ).all()

    user_score = await get_user_missions_score(user_id)

    # 2-4 «Зелёный старт» 🚀, «Сила сотни» 💯, «Eco Legend» 🏆 (1-3)
    await check_credits_achievements(bot, user_id, user_score)

    # 5, 'Тур по зонам 🗺', 'Выполни ≥ 1 миссии в каждой зоне-активации'
    await check_any_mission_achievement(bot, user_id, accepted_submissions, 5)

    # 6, 'Recycler 🔄', 'Сдай вещи в боксы на переработку от Второго Дыхания'
    await check_recycler_achievement(bot, user_id, accepted_submissions, 6)

    # 7, 'Fix-It Pro 🔧', 'Проведи 1 ремонт + 1 апсайкл-проект'
    await check_fix_it_pro_achievement(bot, user_id, accepted_submissions, 7)

    # 8, 'VR-Энтузиаст 🥽', 'Создай ≥ 1 VR-прототип + 1 инсайт'
    pass

    # 9, 'Digital Detoxer 🧹', 'Закрой ≥ 8 пунктов чек-листа Data Detox'
    await check_digital_detoxer_achievement(bot, user_id, accepted_submissions, 9)

    # 10 'Фотохудожник 📸', 'Выполни 3 качественных фото-миссий. (ручная проверка)'
    await check_photo_achievement(bot, user_id, accepted_submissions, 10)

    # 11 'Swap Star ✨', 'Проведи сделку на Эко-свопе и Техносвопе'
    await check_swap_star_achievement(bot, user_id, accepted_submissions, 11)

    # recycler ??

    # «Fix-It Pro» 🔧 (6 - FIX_IT_PRO_ACHIEVEMENT_ID, REPAIR_CAFE_MISSION_ID, UPCYCLING_MISSION_ID)



