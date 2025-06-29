START_TEXT = ("Привет, это Чисто Я Бот 🤖\n\n"
              "Добро пожаловать на <b>Eco Tech Fest</b> — наш выходной фестиваль экотехнологичного образа жизни.")

MAIN_MENU_TEXT = ""

# Menu
GO_TO_MAIN_MENU = "Меню →"
GO_TO_MAIN_MENU_SHORT = "← Меню"
GO_BACK_TO_MAIN_MENU = "← Меню"

MAIN_MAP_TEXT = "Держите карту фестиваля! Также <b>на сцене</b> сегодня вас ждет:\n\n<u>14:00</u> Аукцион\n<u>16:00</u> Хедлайнер DJ Ozero Sveta\n\nВсе активности мероприятия работают до <u>18:00</u>"

SOMETHING_WENT_WRONG = "Что-то пошло не так :(\nПопробуйте еще раз."
CANNOT_HANDLE_SEVERAL_PHOTOS = "Убедитесь, что вы отправляете только одно фото, именно оно будет проверяться модератором. Последующие фото будут проигнорированы."

# Locations
LOCATIONS_MAP_TEXT = ""

PHOTO_SUBMISSION_EXPECTED = (
    "Отправьте фото, на котором видно, что вы выполнили задание."
)
VOICE_SUBMISSION_EXPECTED = (
    "Отправьте голосовое сообщение, в котором расскажете о выполнении задания."
)
TEXT_SUBMISSION_EXPECTED = (
    "Отправьте текстовое сообщение, в котором расскажете о выполнении задания."
)
VIDEO_SUBMISSION_EXPECTED = (
    "Отправьте видео-кружочек, на котором видно, что вы выполнили задание."
)

INTRO_TEXT = "Наш фестиваль включает в себя более 8 интерактивных зон. Выполняя задания (экомиссии), мы собираем горошины Go Green для общего и личного прогресса. Соберите <b>70</b> горошин Go Green и получите <b>спешл напиток от Surf Coffee.</b>\n\nА за успешное прохождение мини-теста забирай аксессуар из переработанного пластика — <b>NFC-брелок от Recycle Object.</b>"

SUBMISSION_REQUEST_TEXT = "Вам пришла новая заявка на проверку задания в рамках эко-миссии <b>«{mission_name}»</b>"
SUBMISSION_SUCCESSFULLY_SENT = (
    "Статус обращения: <b>{request_status}</b>"
)
SUBMISSION_ACCEPTED = (
    "Ваше задание в рамках эко-миссии <b>«{mission_name}»</b> успешно проверено и принято! 🎉\n"
    "Вам начислено <b>{score}</b> 🟢!"
)
SUBMISSION_REJECTED_WITH_MODERATOR = (
    "Ваше задание в рамках эко-миссии <b>«{mission_name}»</b> отклонено. 😔\n"
    "Модератор, отклонивший заявку - <b>{moderator}</b>. Если Вы не согласны с решением, напишите ему."
)
SUBMISSION_REJECTED = (
    "Ваше задание в рамках эко-миссии <b>«{mission_name}»</b> отклонено. 😔\n"
)
VERIFICATION_CODE_SUBMISSION_REJECTED = (
    "<b>Неверный код</i>\n"
    "Вы можете попробовать еще раз!\n"
)

ACCEPT_SUBMISSION = "Принять ✅"
REJECT_SUBMISSION = "Отклонить ❌"

START_CHECKLIST = "Поехали!"

I_VE_DONE_MISSION = "Я выполнил(а) задание ✅"
I_VE_DONE_CHECK_LIST = "Я все отметил(а)"
I_VE_DONE_MISSION_WITH_DIALOG = "Готово! ✅"

NO_VERIFICATION_AND_CHECK_LIST_MISSION_ACCEPTED_INFO = (
    "Отличная работа!\n"
    "Вам начислено {mission_score} 🟢."
)


MISSION_ALREADY_ACCEPTED_ALERT = "Ваше решение уже было проверено и принято! 🎉"
MISSION_IN_PROGRESS_ALERT = (
    "Ваше решение уже было отправлено на проверку. Ожидайте ответа ⏳"
)

SEND_ROBOT_PIC = "🤖 Отправь фото своего робота"

RATE_PICTURE_IF_LIKED = "Отметь фото, если оно тебе понравилось"
LIKE_PICTURE = "Отметить фото ❤️"
PICTURE_HAS_BEEN_LIKED = "Фото отмечено как понравившееся ❤️"

# Personal score
PERSONAL_SCORE_TEXT = (
    "Вы набрали <b>{score}</b> 🟢\n"
    "Командный счет: <b>{team_score}</b> 🟢\n"
)

GET_ACHIEVEMENTS_TEXT = "<b>{achievement_name}</b> выдан!"
EXTRA_INTRO_ACHIEVEMENT_TEXT = "Первый бейдж уже в коллекции. Выполняй эко-миссии — новые карточки будут появляться сами.\n\nСледи за ростом в «Мой прогресс»."
ACHIEVEMENTS_TEXT = "Ниже - бейджи, ✅ - выполнено, ☑️- не выполнено"
ACHIEVEMENT_TEXT = "<b>{achievement_name}</b>\n\n{achievement_description}"
ACHIEVEMENT_RECEIVED_TEXT = "<b>{achievement_name}</b>\n\nВы уже получили этот бейдж! 🎉\n\n{achievement_description}"


END_TEXT = "Спасибо, что были с нами на Eco Tech Fest!\nПоделитесь, пожалуйста, своей <b>обратной связью</b> по мероприятию"
PRE_TEST_TEXT = "Этот мини-тест поможет понять насколько вы ориентируетесь в практиках заботы. За 4 и более верных ответа забирайте NFC-брелок от Recycle Object на стойке регистрации."
# Team score
TEAM_SCORE_TEXT = "Ваша команда набрала <b>{score}</b> 🟢"
TEST_ALREADY_COMPLETED = "Вы уже прошли тест!\nКоличество верных ответов: {score}"

QUESTION_1 = ("<b>Возврат пакетов в Лавке ― это не про лайки, а про циклы</b>\n"
              "Какую маркировку должен иметь пакет-майка, чтобы курьер забрал его на переработку? Можно сдать ненужные пакеты в любом количестве, главное — чистыми и сухими.\n\n"
              "A) 1 PETE\nB) 2 HDPE\nC) 2 PE-HD\nD) Любой полиэтилен")

QUESTION_2 = ("<b>Каждый поисковый запрос — это работа серверов</b>\n"
              "Яндекс совершенствует инфраструктуру дата-центров, чтобы эффективно использовать каждую единицу энергии?\n\n"
              "A) Фрикулинг — охлаждение серверов уличным воздухом\nB) Перевод сервисов на тёмную тему\nC) Установка мониторов пониженной яркости\nD) Перекраска серверных корпусов в зелёный цвет")

QUESTION_3 = ("<b>Наиболее мощным альтернативным источником энергии является солнце.</b>\n"
              "В каком офисе Яндекса установлены солнечные панели?\n\n"
              "A) Москва, Аврора\nB) Белград, Сербская Роза\nC) Казань, Сувар Плаза\nD) Самара, Вертикаль")

QUESTION_4 = ("<b>Дарите вещам второй шанс.</b>\n"
              "Что можно сделать с вещами, которые больше не приносят радости в использовании?\n\n"
              "A) Отнести на своп-вечеринку и обменять на что-то стильное и полезное для себя\nB) Передать в ящик фонда «Второе дыхание» в офисе Яндекса — там принимают одежду, домашний текстиль и многое другое круглый год\nC) Провести апсайклинг или творческое переосмысление старых вещей\nD) Все из вышеперечисленного")


QUESTION_5 = ("<b>Существует принцип \"3R\": Reduce, Reuse, Recycle.</b> Как не стоит поступать с вышедшей из строя домашней техникой согласно данному подходу?\n\n"
              "A) Отнести в офис, там регулярно проходят акции по сбору электроники\nB) Сдать в сервис-центр, починить и пользоваться дальше\nC) Выбросить в ближайший контейнер для смешанных отходов.\nD) Продать или отдать на запчасти через объявления")
# HELPERS
GREAT = "Отлично!"
GOT_IT = "Понятно"
GO_BACK = "← Назад"
CANCEL = "Отменить"
