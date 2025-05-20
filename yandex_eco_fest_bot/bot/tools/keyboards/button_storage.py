from yandex_eco_fest_bot.bot.tools.keyboards.button import Button


class AutoNameButtonMeta(type):
    def __new__(cls, name, bases, namespace):
        for attr_name, value in namespace.items():
            if isinstance(value, Button):
                if not value.name:
                    value.name = attr_name
        return type.__new__(cls, name, bases, namespace)


class ButtonsStorage(metaclass=AutoNameButtonMeta):

    AFTER_START_BUTTON = Button("Даа")

    # Base menu buttons
    LOCATIONS_MAP = Button("📍Карта зон")
    MY_PROGRES = Button("🏆 Мой прогресс")
    TEAM_PROGRES = Button("🌳 Командный вклад")
    HELP = Button("ℹ️ Помощь")
