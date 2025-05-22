from yandex_eco_fest_bot.bot.enums import RequestStatus
from yandex_eco_fest_bot.bot.schemas.missions_display_schema import MissionStatus
from yandex_eco_fest_bot.db.tables import Location, Mission

LOCATIONS_PER_PAGE = 6


def get_page_number_by_location(location: Location):
    return location.order // LOCATIONS_PER_PAGE + 1


def get_mission_display_button(mission_status: MissionStatus) -> str:
    suffix = f": {mission_status.status.label[-1]}" if mission_status.status else ""
    return f"{mission_status.mission.name}{suffix}"
