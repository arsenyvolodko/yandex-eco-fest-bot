from yandex_eco_fest_bot.db.core.async_queryset import AsyncQuerySet
from yandex_eco_fest_bot.db.core.db_manager import db_manager


class AsyncModelManager:
    def __init__(self, model):
        self.model = model

    def filter(self, **kwargs):
        return AsyncQuerySet(self.model).filter(**kwargs)

    def all(self):
        return AsyncQuerySet(self.model).all()

    def first(self, **kwargs):
        return AsyncQuerySet(self.model).filter(**kwargs).first()

    def get(self, **kwargs):
        return AsyncQuerySet(self.model).filter(**kwargs).get()

    def count(self, **kwargs):
        return AsyncQuerySet(self.model).filter(**kwargs).count()

    def create(self, **kwargs):
        return AsyncQuerySet(self.model).create(**kwargs)

    def get_or_create(self, defaults=None, **filters):
        return AsyncQuerySet(self.model).get_or_create(defaults, **filters)

    async def save(self):
        async with db_manager.session_maker() as session:
            session.add(self)
            await session.commit()
            await session.refresh(self)
