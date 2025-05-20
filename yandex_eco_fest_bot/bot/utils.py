from aiogram.types import CallbackQuery, FSInputFile

from yandex_eco_fest_bot.bot import text_storage
from yandex_eco_fest_bot.bot.tools.keyboards.keyboards import (
    get_locations_menu_keyboard,
)
from yandex_eco_fest_bot.core import config
from yandex_eco_fest_bot.core.redis_config import r
from yandex_eco_fest_bot.db.tables import Location, Mission


async def send_locations_with_image(call: CallbackQuery, locations: list[Location]):

    locations_file_id = r.get("LOCATIONS_MAP_FILE_ID")

    if not locations_file_id:
        photo = FSInputFile(config.MEDIA_DIR / "locations_map.png")
        msg = await call.bot.send_photo(
            chat_id=call.message.chat.id,
            photo=photo,
            caption=text_storage.LOCATIONS_MAP_TEXT,
            reply_markup=get_locations_menu_keyboard(locations),
        )
        r.set("LOCATIONS_MAP_FILE_ID", value=msg.photo[-1].file_id)
        return

    await call.bot.send_photo(
        call.message.chat.id,
        locations_file_id,
        caption=text_storage.LOCATIONS_MAP_TEXT,
        reply_markup=get_locations_menu_keyboard(locations),
    )


def get_location_info_text(location: Location) -> str:
    return f"<b>{location.name}</b>\n\n" f"{location.description}"


def get_mission_info_text(mission: Mission) -> str:
    return f"<b>{mission.name}</b>\n\n" f"{mission.description}"
