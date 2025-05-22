from yandex_eco_fest_bot.bot.enums import RequestStatus
from yandex_eco_fest_bot.bot.schemas.base_schema import BaseSchema
from yandex_eco_fest_bot.db.tables import Mission, Location


class MissionStatus(BaseSchema):
    mission: Mission
    status: RequestStatus | None


class LocationMissionsStatus(BaseSchema):
    missions: list[MissionStatus]
    location: Location
