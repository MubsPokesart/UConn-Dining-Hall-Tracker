import asyncio
from dining_hall_handler import get_menu, DiningHallType

DINING_HALLS = [DiningHallType.CONNECTICUT, DiningHallType.MCMAHON, DiningHallType.NORTH, DiningHallType.TOWERS, DiningHallType.WHITNEY, DiningHallType.SOUTH, DiningHallType.PUTNAM, DiningHallType.NORTHWEST]

def test_dining_hall_handler():
    # Get the menu for each dining hall
    tasks = [get_menu(dining_hall) for dining_hall in DINING_HALLS]
    return tasks

print(test_dining_hall_handler())