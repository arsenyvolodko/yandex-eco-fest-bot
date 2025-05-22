from yandex_eco_fest_bot.bot.schemas.base_schema import BaseSchema
from yandex_eco_fest_bot.db.tables import Achievement


class AchievementStatus(BaseSchema):
    achievement: Achievement
    is_succeeded: bool
