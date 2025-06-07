from yandex_eco_fest_bot.bot.enums import MissionVerificationMethod
from yandex_eco_fest_bot.bot.tools import states

CHECK_LIST_POINT_SCORE = 1

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
