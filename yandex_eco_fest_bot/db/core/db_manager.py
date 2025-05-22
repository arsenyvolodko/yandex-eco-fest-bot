from sqlalchemy.ext.asyncio import async_sessionmaker

from yandex_eco_fest_bot.core.config import DATABASE_URL
from yandex_eco_fest_bot.db.core.base_table import BaseTable
from yandex_eco_fest_bot.db.core.engine_manager import EngineManager
from yandex_eco_fest_bot.db.tables import (  # noqa
    Location,
    Mission,
    User,
    UserMissionSubmission,
    Achievement,
    UserAchievement,
)


class DBManager:
    def __init__(self):
        self.session_maker = None

    async def init(self):
        async with EngineManager(DATABASE_URL) as engine:
            self.session_maker = async_sessionmaker(engine, expire_on_commit=False)
            async with engine.begin() as conn:
                await conn.run_sync(BaseTable.metadata.create_all)


db_manager = DBManager()
