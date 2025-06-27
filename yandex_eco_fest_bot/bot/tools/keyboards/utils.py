from yandex_eco_fest_bot.bot.enums import RequestStatus
from yandex_eco_fest_bot.bot.schemas.missions_display_schema import MissionStatus


def get_mission_display_button(mission_status: MissionStatus) -> str:
    if mission_status.status == RequestStatus.ACCEPTED:
        text = "Задание выполнено"
    else:
        text = "Перейти к заданию"
    suffix = f": {mission_status.status.label[-1]}" if mission_status.status else ""
    return f"{text} {suffix}"
