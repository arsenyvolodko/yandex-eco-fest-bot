from yandex_eco_fest_bot.bot.enums import MissionVerificationMethod
from yandex_eco_fest_bot.bot.tools import states
from yandex_eco_fest_bot.bot.tools.keyboards.button_storage import ButtonsStorage
from yandex_eco_fest_bot.core.config import MEDIA_DIR

CHECK_LIST_POINT_SCORE = 5

VERIFICATION_METHOD_TO_STATE = {
    MissionVerificationMethod.PHOTO: states.WAITING_FOR_PICTURE_SUBMISSION,
    MissionVerificationMethod.TEXT: states.WAITING_FOR_TEXT_SUBMISSION,
    MissionVerificationMethod.VOICE: states.WAITING_FOR_VOICE_SUBMISSION,
    MissionVerificationMethod.VIDEO: states.WAITING_FOR_VIDEO_SUBMISSION,
    MissionVerificationMethod.VERIFICATION_CODE: states.WAITING_FOR_VERIFICATION_CODE_SUBMISSION,
}

CAPTION_TYPE_VERIFICATION_METHODS = {
    MissionVerificationMethod.PHOTO,
    MissionVerificationMethod.VOICE,
}

CHECK_LIST_QUESTIONS = [
    "Я собрал(а) мусор в лесу",
    "Я собрал(а) мусор на пляже",
    "Я собрал(а) мусор в парке",
    "Я собрал(а) мусор в городе",
    "Я посадил(а) дерево",
    "Я высадил(а) цветы",
    "Я покрасил(а) забор",
    "Я покрасил(а) лавочку",
    "Я покрасил(а) урну",
]

ADMIN_IDS = [506954303, 379924180]
LOCATIONS_MEDIA_DIR = f"{MEDIA_DIR}/locations"
ACHIEVEMENTS_MEDIA_DIR = f"{MEDIA_DIR}/achievements"
PERSONAL_WORK_MEDIA_URL = f"{MEDIA_DIR}/personal_work.png"
TEAM_WORK_MEDIA_URL = f"{MEDIA_DIR}/team_work.png"
MAIN_MENU_MEDIA_URL = f"{MEDIA_DIR}/main_menu_pic.png"
PROGRAM_MEDIA_URL = f"{MEDIA_DIR}/program.png"

MAIN_MAP_MEDIA_URL = f"{MEDIA_DIR}/map_small_.png"
BIG_MAP_MEDIA_URL = f"{MEDIA_DIR}/map_full.png"

COMMON_PICTURES_CHAT_ID = -1002672226725  # https://t.me/+MI4JcU5xwSc4NTYy
KIDS_ROBOTS_CHAT_ID = -1002682842161  # https://t.me/+9sNd3OtsEgAzMzFi

LOCATIONS_TOTAL_COUNT = 13
ROBOLAB_KIDS_LOCATION_ID = 11

TEST_Q_1_BUTTONS = {
    ButtonsStorage.OPTION_1_1.callback,
    ButtonsStorage.OPTION_1_2.callback,
    ButtonsStorage.OPTION_1_3.callback,
    ButtonsStorage.OPTION_1_4.callback,
}

TEST_Q_2_BUTTONS = {
    ButtonsStorage.OPTION_2_1.callback,
    ButtonsStorage.OPTION_2_2.callback,
    ButtonsStorage.OPTION_2_3.callback,
    ButtonsStorage.OPTION_2_4.callback,
}

TEST_Q_3_BUTTONS = {
    ButtonsStorage.OPTION_3_1.callback,
    ButtonsStorage.OPTION_3_2.callback,
    ButtonsStorage.OPTION_3_3.callback,
    ButtonsStorage.OPTION_3_4.callback,
}
TEST_Q_4_BUTTONS = {
    ButtonsStorage.OPTION_4_1.callback,
    ButtonsStorage.OPTION_4_2.callback,
    ButtonsStorage.OPTION_4_3.callback,
    ButtonsStorage.OPTION_4_4.callback,
}

TEST_Q_5_BUTTONS = {
    ButtonsStorage.OPTION_5_1.callback,
    ButtonsStorage.OPTION_5_2.callback,
    ButtonsStorage.OPTION_5_3.callback,
    ButtonsStorage.OPTION_5_4.callback,
}