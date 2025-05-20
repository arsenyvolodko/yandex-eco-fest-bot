from sqlalchemy import select, func

from yandex_eco_fest_bot.db.core.db_manager import db_manager


class AsyncQuerySet:
    def __init__(self, model):
        self.model = model
        self._filters = {}

    def filter(self, **kwargs):
        self._filters.update(kwargs)
        return self

    async def all(self):
        async with db_manager.session_maker() as session:
            stmt = select(self.model).filter_by(**self._filters)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalars().all()

    async def first(self):
        async with db_manager.session_maker() as session:
            stmt = select(self.model).filter_by(**self._filters).limit(1)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one_or_none()

    async def get(self):
        async with db_manager.session_maker() as session:
            stmt = select(self.model).filter_by(**self._filters)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one_or_none()

    async def count(self):
        async with db_manager.session_maker() as session:
            stmt = select(func.count()).select_from(self.model).filter_by(**self._filters)
            result = await session.execute(stmt)
            return result.scalar_one()

    async def create(self, **kwargs):
        async with db_manager.session_maker() as session:
            obj = self.model(**kwargs)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def get_or_create(self, defaults=None, **filters):
        async with db_manager.session_maker() as session:
            obj = await self.filter(**filters).first()
            if obj:
                return obj, False
            else:
                defaults = defaults or {}
                obj = self.model(**{**filters, **defaults})
                session.add(obj)
                await session.commit()
                await session.refresh(obj)
                return obj, True

