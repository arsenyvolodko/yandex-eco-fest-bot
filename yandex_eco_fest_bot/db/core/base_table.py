from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr

from yandex_eco_fest_bot.db.core.objects_descriptor import ObjectsDescriptor


class BaseTable(AsyncAttrs, DeclarativeBase):
    objects = ObjectsDescriptor()

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __repr__(self):
        return self.__str__()

    async def save(self):
        from yandex_eco_fest_bot.db.core.db_manager import db_manager

        async with db_manager.session_maker() as session:
            session.add(self)
            await session.commit()
            await session.refresh(self)

    async def delete(self):
        from yandex_eco_fest_bot.db.core.db_manager import db_manager

        async with db_manager.session_maker() as session:
            await session.delete(self)
            await session.commit()
