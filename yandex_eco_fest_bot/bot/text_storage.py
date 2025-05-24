START_TEXT = "Привет! Меня зовут Валли … 🤖.  Добро пожаловать на такое-то событие … . Тебя ждут х зон, более у эко-миссий. Давай вместе [про геймификацию] . Ты готов(а) … ?"
AFTER_START_TEXT = "Рад знакомству {name}! Самое время … ."

MAIN_MENU_TEXT = "[Info text]"

# Menu
GO_TO_MAIN_MENU = "Перейти в меню"
GO_TO_MAIN_MENU_SHORT = "В меню ⤵️"
GO_BACK_TO_MAIN_MENU = "Вернуться в меню ⤵️"

SOMETHING_WENT_WRONG = "Что-то пошло не так :(\nПопробуйте еще раз."
CANNOT_HANDLE_SEVERAL_PHOTOS = "Убедитесь, что вы отправляете только одно фото, именно оно будет проверяться модератором. Последующие фото будут проигнорированы."

# Locations
LOCATIONS_MAP_TEXT = "[Locations map text]"

PHOTO_SUBMISSION_EXPECTED = "Отправьте фото, на котором видно, что вы выполнили задание."
VOICE_SUBMISSION_EXPECTED = "Отправьте голосовое сообщение, в котором расскажете о выполнении задания."
TEXT_SUBMISSION_EXPECTED = "Отправьте текстовое сообщение, в котором расскажете о выполнении задания."
VIDEO_SUBMISSION_EXPECTED = "Отправьте видео-кружочек, на котором видно, что вы выполнили задание."


SUBMISSION_REQUEST_TEXT = "Вам пришла новая заявка на проверку задания от @{username} в рамках эко-миссии <b>«{mission_name}»</b>"
SUBMISSION_SUCCESSFULLY_SENT = (
    "Заявка на проверку задания успешно отправлена.\n"
    "Статус обращения: <b>{request_status}</b>"
)
SUBMISSION_ACCEPTED = (
    "Ваше задание в рамках эко-миссии <b>«{mission_name}»</b> успешно проверено и принято! 🎉\n"
    "Вам начислено <b>{score}</b> 🌱кредитов!"
)
SUBMISSION_REJECTED = (
    "Ваше задание в рамках эко-миссии <b>«{mission_name}»</b> отклонено. 😔\n"
    "Модератор, отклонивший заявку - <b>{moderator}</b>. Если Вы не согласны с решением, напишите ему."
)

ACCEPT_SUBMISSION = "Принять ✅"
REJECT_SUBMISSION = "Отклонить ❌"

MISSION_ACCEPTED_INFO = (
    "<b>{mission_name}</b>\n\n"
    "Ваше решение принято модераторами 🎉.\n"
    "Вам начислено {mission_score} 🌱кредитов.\n"
    "Вы не можете пройти эту эко-миссию повторно\n\n"
    "{mission_description}"
)

MISSION_PENDING_INFO = (
    "<b>{mission_name}</b>\n\n"
    "Ваше решение отправлено модераторам на проверку. Ожидайте ответа ⏳\n\n"
    "{mission_description}"
)

MISSION_DECLINED_INFO = (
    "<b>{mission_name}</b>\n\n"
    "Ваше решение отклонено модераторами ❌.\n"
    "Вы можете попробовать снова!\n\n"
    "{mission_description}"
)

MISSION_ALREADY_ACCEPTED_ALERT = "Ваше решение уже было проверено и принято! 🎉"
MISSION_IN_PROGRESS_ALERT = (
    "Ваше решение уже было отправлено на проверку. Ожидайте ответа ⏳"
)

# Personal score
PERSONAL_SCORE_TEXT = (
    "У тебя <b>{score}</b> 🌱кредитов\n\n" "Выполняй миссии, получай бейджи.."
)

ACHIEVEMENTS_TEXT = "Ниже - бейджи, ✅ - выполнено, ☑️- не выполнено"
ACHIEVEMENT_TEXT = "<b>{achievement_name}</b>\n\n{achievement_description}"
ACHIEVEMENT_RECEIVED_TEXT = "<b>{achievement_name}</b>\n\nТы уже получил этот бейдж! 🎉\n\n{achievement_description}"


# Team score
TEAM_SCORE_TEXT = "Ваша команда набрала <b>{score}</b> 🌱кредитов"

# HELPERS
GREAT = "Отлично! 👍"
GOT_IT = "Понятно 👌"
GO_BACK = "Назад ⤵️"
NEXT_PAGE = "Вправо ➡️"
PREV_PAGE = "⬅️ Влево"
CANCEL = "Отменить 🚫"
