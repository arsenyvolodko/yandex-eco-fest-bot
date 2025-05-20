from yandex_eco_fest_bot.db.tables import Location

LOCATIONS_PER_PAGE = 6


def get_page_number_by_location(location: Location):
    return location.order // LOCATIONS_PER_PAGE + 1
