from datetime import datetime


def sort_cactuses(cactuses, sort_key):
    """Sort cactuses based on the given key"""
    cactus_list = list(cactuses.keys())

    if sort_key == "По имени":
        cactus_list.sort()
    elif sort_key == "По частоте полива":
        cactus_list.sort(key=lambda x: cactuses[x]["watering_frequency"])
    elif sort_key == "По последнему поливу":
        cactus_list.sort(key=lambda x: get_last_watering_date(cactuses, x), reverse=True)

    return cactus_list


def get_last_watering_date(cactuses, cactus_name):
    """Get last watering date for sorting"""
    watering = cactuses[cactus_name]["watering"]
    if watering:
        return datetime.strptime(watering[-1]["date"], "%Y-%m-%d %H:%M")
    return datetime.min