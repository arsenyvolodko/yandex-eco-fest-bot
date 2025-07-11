from enum import Enum


class MissionVerificationMethod(Enum):
    PHOTO = "photo"
    TEXT = "text"
    VOICE = "voice"
    VIDEO = "video"
    VERIFICATION_CODE = "verification_code"
    NO_VERIFICATION = "no_verification"
    CHECK_LIST = "check_list"
    NO_VERIFICATION_DIALOG = "dialog"
