from yandex_eco_fest_bot.bot.enums import MissionVerificationMethod
from yandex_eco_fest_bot.bot.tools import states
from yandex_eco_fest_bot.bot.tools.keyboards.button_storage import ButtonsStorage
from yandex_eco_fest_bot.core.config import MEDIA_DIR

CHECK_LIST_POINT_SCORE = 2

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

LOCATIONS_MEDIA_DIR = f"{MEDIA_DIR}/locations"
ACHIEVEMENTS_MEDIA_DIR = f"{MEDIA_DIR}/achievements"
PERSONAL_WORK_MEDIA_URL = f"{MEDIA_DIR}/personal_work.png"
TEAM_WORK_MEDIA_URL = f"{MEDIA_DIR}/team_work.png"
MAP_MEDIA_URL = f"{MEDIA_DIR}/map.png"
MAIN_MENU_MEDIA_URL = f"{MEDIA_DIR}/main.png"

COMMON_PICTURES_CHAT_ID = -1002672226725  # https://t.me/+MI4JcU5xwSc4NTYy
KIDS_ROBOTS_CHAT_ID = -1002682842161  # https://t.me/+9sNd3OtsEgAzMzFi

VERIFICATION_METHOD_TEXT = {
    MissionVerificationMethod.PHOTO: "Для решения задания отправьте фото, на котором видно, что вы выполнили задание.",
    MissionVerificationMethod.VOICE: "Для решения задания отправьте голосовое сообщение, в котором расскажете о выполнении задания.",
    MissionVerificationMethod.TEXT: "Для решения задания отправьте текстовое сообщение, в котором расскажете о выполнении задания.",
    MissionVerificationMethod.VIDEO: "Для решения задания отправьте видео-кружочек, на котором видно, что вы выполнили задание.",
    MissionVerificationMethod.VERIFICATION_CODE: "Для решения задания отправьте код, который вы получили от модератора.",
    # MissionVerificationMethod.NO_VERIFICATION: "Когда выполнишь задание нажми ",
    MissionVerificationMethod.CHECK_LIST: "Для решения задания отметьте выполненные пункты в чек-листе.",
    # MissionVerificationMethod.NO_VERIFICATION_DIALOG: "",
}

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
    ButtonsStorage.OPTION_4_5.callback,
}

TEST_Q_5_BUTTONS = {
    ButtonsStorage.OPTION_5_1.callback,
    ButtonsStorage.OPTION_5_2.callback,
    ButtonsStorage.OPTION_5_3.callback,
    ButtonsStorage.OPTION_5_4.callback,
    ButtonsStorage.OPTION_5_5.callback,
}