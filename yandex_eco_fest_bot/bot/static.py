from yandex_eco_fest_bot.bot.enums import MissionVerificationMethod
from yandex_eco_fest_bot.bot.tools import states

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
