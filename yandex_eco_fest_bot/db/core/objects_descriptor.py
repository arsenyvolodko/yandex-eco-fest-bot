class ObjectsDescriptor:
    def __get__(self, instance, owner):
        from yandex_eco_fest_bot.db.core.model_manager import AsyncModelManager

        return AsyncModelManager(owner)
