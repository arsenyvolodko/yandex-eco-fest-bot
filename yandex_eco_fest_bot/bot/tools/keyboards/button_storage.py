from yandex_eco_fest_bot.bot.tools.keyboards.button import Button


class AutoNameButtonMeta(type):
    def __new__(cls, name, bases, namespace):
        for attr_name, value in namespace.items():
            if isinstance(value, Button):
                if not value.name:
                    value.name = attr_name
        return type.__new__(cls, name, bases, namespace)


class ButtonsStorage(metaclass=AutoNameButtonMeta):

    AFTER_START_BUTTON = Button("Привет!")
    THANKS_BUTTON = Button("Спасибо!")
    GET_START_ACHIEVEMENT = Button("Поехали!")
    HIDE_MESSAGE = Button("Скрыть сообщение")

    # Base menu buttons
    LOCATIONS_MAP = Button("Экомиссии →")
    MY_PROGRES = Button("Мой прогресс →")
    TEAM_PROGRES = Button("Командный вклад")
    START_TEST_1 = Button("Тест")
    START_TEST_2 = Button("Начать →")
    HELP = Button("Помощь")
    QUEST_BUTTON = Button("Квест")
    MAIN_MAP = Button("Карта")

    ADMIN_BUTTON = Button("Отправить сообщение всем")
    GO_TO_ACHIEVEMENTS_BUTTON = Button("Бейджи →")

    OPTION_1_1 = Button("A")
    OPTION_1_2 = Button("B")
    OPTION_1_3 = Button("C")
    OPTION_1_4 = Button("D")

    OPTION_2_1 = Button("A")
    OPTION_2_2 = Button("B")
    OPTION_2_3 = Button("C")
    OPTION_2_4 = Button("D")

    OPTION_3_1 = Button("A")
    OPTION_3_2 = Button("B")
    OPTION_3_3 = Button("C")
    OPTION_3_4 = Button("D")

    OPTION_4_1 = Button("A")
    OPTION_4_2 = Button("B")
    OPTION_4_3 = Button("C")
    OPTION_4_4 = Button("D")

    OPTION_5_1 = Button("A")
    OPTION_5_2 = Button("B")
    OPTION_5_3 = Button("C")
    OPTION_5_4 = Button("D")
