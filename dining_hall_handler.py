import re
import aiohttp
import asyncio
import pendulum
from enum import Enum
from datetime import datetime
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Dict, TypedDict, Literal, Optional, Any


"""

All code below is converted from the original blueplate handlers made by iefa labs
Most of the code is the same in function, but has been converted from tyescript to python
Minor changes have been made to incoporate Connecticut Hall data and nutritional data

Credits to iefa labs for the original code: https://www.npmjs.com/package/@ilefa/blueplate/v/1.1.2?activeTab=code under GPL-3.0 License

"""

@dataclass
class Station:
    name: str
    options: List[str]

@dataclass
class Meal:
    name: str
    stations: List[Station]

@dataclass
class Location:
    id: str
    name: str
    latitude: float
    longitude: float
    address: str
    maps: str

@dataclass
class DiningHall:
    name: str
    late_night: bool
    location: Location

class DiningHallStatus(str, Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    BRUNCH = "Brunch"
    DINNER = "Dinner"
    LATE_NIGHT = "Late Night"
    BETWEEN_MEALS = "Between Meals"
    CLOSED = "Closed"

class ActiveDiningStatuses(str, Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    BRUNCH = "Brunch"
    DINNER = "Dinner"
    LATE_NIGHT = "Late Night"

class DiningHallType(str, Enum):
    CONNECTICUT = "Connecticut"
    MCMAHON = "McMahon"
    NORTH = "North"
    NORTHWEST = "Northwest"
    PUTNAM = "Putnam"
    SOUTH = "South"
    TOWERS = "Towers"
    WHITNEY = "Whitney"

@dataclass
class DiningHallResponse(DiningHall):
    time: datetime
    meals: List[Meal]
    type: DiningHallType
    status: DiningHallStatus

@dataclass
class DiningHallHours:
    start: str
    end: str
    days: List[int]

# Type aliases using TypedDict
DiningHallHoursMap = TypedDict('DiningHallHoursMap', {
    status: List[DiningHallHours] for status in ActiveDiningStatuses
})

DiningHallSchedules = TypedDict('DiningHallSchedules', {
    hall_type: DiningHallHoursMap for hall_type in DiningHallType
})

# Dining Halls data
DINING_HALLS: Dict[str, DiningHall] = {
    'CONNECTICUT': DiningHall(
        name='Connecticut',
        late_night=False,
        location=Location(
            id='03',
            name='Connecticut+Dining+Hall',
            latitude=41.8052246,
            longitude=-72.2487484,
            address='55 Gilbert Rd, Storrs, CT 06269',
            maps='https://www.google.com/maps/place/New+South+Campus+Residence+Hall/@41.8052246,-72.2487484,20.25z/data=!4m6!3m5!1s0x89e68baab0ff5a0b:0x94073d5895c9eafd!8m2!3d41.805416!4d-72.2485399!16s%2Fg%2F11vb9tx92m?entry=ttu&g_ep=EgoyMDI0MTAyMy4wIKXMDSoASAFQAw%3D%3D'
        )
    ),
    'MCMAHON': DiningHall(
        name='McMahon',
        late_night=False,
        location=Location(
            id='05',
            name='McMahon+Dining+Hall',
            latitude=41.803548,
            longitude=-72.252385,
            address='2011 Hillside Rd, Storrs, CT, 06269',
            maps='https://www.google.com/maps/place/McMahon+Dining+Hall/@41.8035583,-72.2546329,17z/data=!3m1!4b1!4m5!3m4!1s0x89e68a3d9478806f:0xc7f055938ed1d0a6!8m2!3d41.8033822!4d-72.2522574'
        )
    ),
    'NORTH': DiningHall(
        name='North',
        late_night=False,
        location=Location(
            id='07',
            name='North+Campus+Dining+Hall',
            latitude=41.812185,
            longitude=-72.258381,
            address='82 N Eagleville Rd, Storrs, CT 06269',
            maps='https://www.google.com/maps/place/North+Campus+Dining+Hall/@41.8118133,-72.2580436,20.01z/data=!4m12!1m6!3m5!1s0x89e68a3d9478806f:0xc7f055938ed1d0a6!2sMcMahon+Dining+Hall!8m2!3d41.8033822!4d-72.2522574!3m4!1s0x0:0xb9f08e6948417f21!8m2!3d41.8121366!4d-72.2585661'
        )
    ),
    'NORTHWEST': DiningHall(
        name='Northwest',
        late_night=True,
        location=Location(
            id='15',
            name='Northwest+Marketplace',
            latitude=41.811441,
            longitude=-72.259667,
            address='N Eagleville Rd, Storrs, CT, 06269',
            maps='https://www.google.com/maps/place/Northwest+Dining+Hall/@41.8112212,-72.2599746,20.01z/data=!3m1!5s0x89e68a3879629c67:0x409c2613356c4ee1!4m5!3m4!1s0x0:0xe476d288c7ffdf1c!8m2!3d41.811443!4d-72.259743'
        )
    ),
    'PUTNAM': DiningHall(
        name='Putnam',
        late_night=False,
        location=Location(
            id='06',
            name='Putnam+Dining+Hall',
            latitude=41.805151,
            longitude=-72.258880,
            address='2358 Alumni Dr, Storrs, CT 06269',
            maps='https://www.google.com/maps/place/Putnam+Refectory/@41.8058232,-72.2599886,17.97z/data=!3m1!5s0x89e68a3f9416b0d3:0x4fa606fb32492bef!4m5!3m4!1s0x0:0xe102fa527107db81!8m2!3d41.805226!4d-72.2589772'
        )
    ),
    'SOUTH': DiningHall(
        name='South',
        late_night=True,
        location=Location(
            id='16',
            name='South+Campus+Marketplace',
            latitude=41.803892,
            longitude=-72.248538,
            address='Lewis B. Rome Commons, Storrs, CT 06269',
            maps='https://www.google.com/maps/place/South+Campus+Dining+Hall/@41.8038295,-72.2503784,17.97z/data=!4m5!3m4!1s0x0:0x78bae9af27afcc79!8m2!3d41.8037265!4d-72.2486193'
        )
    ),
    'TOWERS': DiningHall(
        name='Towers',
        late_night=False,
        location=Location(
            id='42',
            name='Gelfenbien+Commons,%20Halal+%26+Kosher',
            latitude=41.813455,
            longitude=-72.254368,
            address='3384 Tower Loop Rd, Storrs, CT 06269',
            maps='https://www.google.com/maps/place/41%C2%B048\'48.4%22N+72%C2%B015\'15.9%22W/@41.8135159,-72.253911,19.46z/data=!4m6!3m5!1s0x89e68a374c6ed731:0xbdf26ec0e2e34ec4!7e2!8m2!3d41.8134318!4d-72.2544378'
        )
    ),
    'WHITNEY': DiningHall(
        name='Whitney',
        late_night=False,
        location=Location(
            id='01',
            name='Whitney+Dining+Hall',
            latitude=41.809891,
            longitude=-72.247374,
            address='1356 Storrs Rd, Storrs, CT 06269',
            maps='https://www.google.com/maps/place/Edwina+Whitney+Residence+Hall/@41.8101301,-72.2475367,19z/data=!4m5!3m4!1s0x89e68a253a40d1e5:0xa1fbff3b6e368cf4!8m2!3d41.8099587!4d-72.2472346'
        )
    )
}

# Day constants
LATE_NIGHT_DINING_HALLS = [DiningHallType.SOUTH, DiningHallType.NORTHWEST]
LATE_NIGHT_WEEKDAYS = [0, 1, 2, 3, 4]
ALL_DAYS = [0, 1, 2, 3, 4, 5, 6]
WEEKDAYS = [1, 2, 3, 4, 5]
WEEKENDS = [6, 0]

# Dining Hall Hours
DINING_HALL_HOURS: Dict[str, Dict[str, List[DiningHallHours]]] = {
    'CONNECTICUT': {
        'BREAKFAST': [DiningHallHours(start='7:00 AM', end='10:45 AM', days=WEEKDAYS)],
        'BRUNCH': [DiningHallHours(start='10:30 AM', end='2:30 PM', days=WEEKENDS)],
        'LATE_NIGHT': [],
        'LUNCH': [DiningHallHours(start='11:00 AM', end='2:30 PM', days=WEEKDAYS)],
        'DINNER': [DiningHallHours(start='4:00 PM', end='7:15 PM', days=ALL_DAYS)],
    },
    'MCMAHON': {
        'BREAKFAST': [DiningHallHours(start='7:00 AM', end='10:45 AM', days=WEEKDAYS)],
        'BRUNCH': [DiningHallHours(start='10:30 AM', end='2:00 PM', days=WEEKENDS)],
        'LATE_NIGHT': [],
        'LUNCH': [DiningHallHours(start='11:00 AM', end='2:00 PM', days=WEEKDAYS)],
        'DINNER': [DiningHallHours(start='3:30 PM', end='7:15 PM', days=ALL_DAYS)],
    },
    'NORTH': {
        'BREAKFAST': [DiningHallHours(start='7:00 AM', end='10:45 AM', days=WEEKDAYS)],
        'BRUNCH': [DiningHallHours(start='10:30 AM', end='3:00 PM', days=WEEKENDS)],
        'LATE_NIGHT': [],
        'LUNCH': [DiningHallHours(start='11:00 AM', end='3:00 PM', days=WEEKDAYS)],
        'DINNER': [DiningHallHours(start='4:30 PM', end='7:15 PM', days=ALL_DAYS)],
    },
    'NORTHWEST': {
        'BREAKFAST': [DiningHallHours(start='7:00 AM', end='10:45 AM', days=WEEKDAYS)],
        'BRUNCH': [DiningHallHours(start='10:30 AM', end='2:15 PM', days=WEEKENDS)],
        'LUNCH': [DiningHallHours(start='11:00 AM', end='2:15 PM', days=WEEKDAYS)],
        'DINNER': [
            DiningHallHours(start='3:45 PM', end='7:15 PM', days=WEEKDAYS),
            DiningHallHours(start='3:45 PM', end='7:15 PM', days=WEEKENDS)
        ],
        'LATE_NIGHT': [DiningHallHours(start='7:15 PM', end='10:00 PM', days=LATE_NIGHT_WEEKDAYS)]
    },
    'PUTNAM': {
        'BREAKFAST': [DiningHallHours(start='7:00 AM', end='10:45 AM', days=WEEKDAYS)],
        'BRUNCH': [DiningHallHours(start='9:30 AM', end='2:30 PM', days=WEEKENDS)],
        'LATE_NIGHT': [],
        'LUNCH': [DiningHallHours(start='11:00 AM', end='2:30 PM', days=WEEKDAYS)],
        'DINNER': [DiningHallHours(start='4:00 PM', end='7:15 PM', days=ALL_DAYS)],
    },
    'SOUTH': {
        'BREAKFAST': [
            DiningHallHours(start='7:00 AM', end='10:45 AM', days=WEEKDAYS),
            DiningHallHours(start='7:00 AM', end='9:30 AM', days=[6]),
            DiningHallHours(start='8:00 AM', end='9:30 AM', days=[0])
        ],
        'BRUNCH': [DiningHallHours(start='9:30 AM', end='2:15 PM', days=WEEKENDS)],
        'LUNCH': [DiningHallHours(start='11:00 AM', end='2:00 PM', days=WEEKDAYS)],
        'DINNER': [
            DiningHallHours(start='3:45 PM', end='7:15 PM', days=WEEKDAYS),
            DiningHallHours(start='3:45 PM', end='7:15 PM', days=WEEKENDS)
        ],
        'LATE_NIGHT': [DiningHallHours(start='7:15 PM', end='10:00 PM', days=LATE_NIGHT_WEEKDAYS)]
    },
    'TOWERS': {
        'BREAKFAST': [DiningHallHours(start='7:00 AM', end='10:45 AM', days=WEEKDAYS)],
        'BRUNCH': [DiningHallHours(start='9:30 AM', end='2:30 PM', days=WEEKENDS)],
        'LATE_NIGHT': [],
        'LUNCH': [DiningHallHours(start='11:00 AM', end='2:30 PM', days=WEEKDAYS)],
        'DINNER': [DiningHallHours(start='4:00 PM', end='7:15 PM', days=ALL_DAYS)],
    },
    'WHITNEY': {
        'BREAKFAST': [DiningHallHours(start='7:00 AM', end='10:45 AM', days=WEEKDAYS)],
        'BRUNCH': [DiningHallHours(start='10:30 AM', end='3:00 PM', days=WEEKENDS)],
        'LATE_NIGHT': [],
        'LUNCH': [DiningHallHours(start='11:00 AM', end='3:00 PM', days=WEEKDAYS)],
        'DINNER': [DiningHallHours(start='4:30 PM', end='7:15 PM', days=ALL_DAYS)],
    },
}

def get_enum_key_by_enum_value(target: Any, value: str, case_sensitive: bool = True) -> Optional[str]:
    """Get enum key from value."""
    if not case_sensitive:
        value = value.lower()
        keys = [k for k in target.__members__ 
               if target[k].value.lower() == value]
    else:
        keys = [k for k in target.__members__ 
               if target[k].value == value]
    return keys[0] if keys else None

def get_dining_hall_status(hall_type: DiningHallType, date: datetime = None) -> str:
    """Get dining hall status for given time."""
    if date is None:
        date = datetime.now()
        
    key = get_enum_key_by_enum_value(DiningHallType, hall_type)
    hours = DINING_HALL_HOURS[key]
    
    current_time = pendulum.instance(date)
    
    # Check each meal period
    for status, ranges in hours.items():
        for time_range in ranges:
            if date.weekday() in time_range.days:
                start = pendulum.from_format(time_range.start, 'h:mm A')
                end = pendulum.from_format(time_range.end, 'h:mm A')
                
                start = start.set(year=date.year, month=date.month, day=date.day)
                end = end.set(year=date.year, month=date.month, day=date.day)
                
                if start <= current_time <= end:
                    return status
    
    # Check if between meals
    breakfast = next((range for range in hours.get('BREAKFAST', [])
                     if date.weekday() in range.days), None)
    if not breakfast:
        return 'CLOSED'
        
    # Get earliest start and latest end times
    start_time = pendulum.from_format(breakfast.start, 'h:mm A')
    latest_end = max(pendulum.from_format(range.end, 'h:mm A')
                    for status_ranges in hours.values()
                    for range in status_ranges
                    if date.weekday() in range.days)
    
    start_time = start_time.set(year=date.year, month=date.month, day=date.day)
    latest_end = latest_end.set(year=date.year, month=date.month, day=date.day)
    
    if start_time <= current_time <= latest_end:
        return 'BETWEEN_MEALS'
    
    return 'CLOSED'

def capitalize_first(text: str) -> str:
    """Capitalize first letter of each word."""
    return ' '.join(word.capitalize() for word in text.lower().split())

async def get_menu_urls(html: str) -> List[str]:
   """Extract all longmenu.aspx URLs from initial page."""
   soup = BeautifulSoup(html, 'html.parser')
   menu_links = soup.find_all('a', href=lambda x: x and 'longmenu.aspx' in x)
   return [link['href'] for link in menu_links]
       
async def get_nutrition_info(base_url: str, nutrition_url: str) -> Dict:
   """Get nutrition info from label.aspx page."""
   async with aiohttp.ClientSession() as session:
       async with session.get(f"{base_url}/{nutrition_url}") as response:
           html = await response.text()
           soup = BeautifulSoup(html, 'html.parser')
           
           nutrition = {}
           facts_table = soup.find('table', class_='nutfactsfonts')
           if facts_table:
               # Get calories
               calories = facts_table.find('td', class_='nutfactscaloriesval')
               if calories:
                   nutrition['calories'] = calories.text.strip()
               
               # Get macros
               for nutrient in facts_table.find_all('span', class_='nutfactstopnutrient'): 
                   text = nutrient.get_text(strip=True)
                   # Handle special cases 
                   if 'Total Fat' in text:
                       nutrition['total_fat'] = text.replace('Total Fat', '').strip()
                   elif 'Saturated Fat' in text:
                       nutrition['saturated_fat'] = text.replace('Saturated Fat', '').strip()
                   elif 'Trans Fat' in text:
                       nutrition['trans_fat'] = text.replace('Trans Fat', '').strip()
                   elif 'Cholesterol' in text:
                       nutrition['cholesterol'] = text.replace('Cholesterol', '').strip()
                   elif 'Sodium' in text:
                       nutrition['sodium'] = text.replace('Sodium', '').strip()
                   elif 'Total Carbohydrate' in text:
                       nutrition['total_carbs'] = text.replace('Total Carbohydrate', '').strip()
                   elif 'Dietary Fiber' in text:
                       nutrition['fiber'] = text.replace('Dietary Fiber', '').strip()
                   elif 'Total Sugars' in text:
                       nutrition['sugars'] = text.replace('Total Sugars', '').strip()
                   elif 'Added Sugars' in text:
                       nutrition['added_sugars'] = text.replace('Added Sugars', '').strip()
                   elif 'Protein' in text:
                       nutrition['protein'] = text.replace('Protein', '').strip()
               
               """# Get vitamins/minerals
               nutrients_table = facts_table.find('table', {'width': '100%', 'align': 'left'})
               if nutrients_table:
                   for nutrient in nutrients_table.find_all('span', class_='nutfactstopnutrient'):
                       text = nutrient.text.strip()
                       if text:
                           name = text.split()[0]
                           value = text.split()[-1]
                           nutrition[name.lower()] = value"""
           
           # Get allergens
           allergens = soup.find('span', class_='labelallergensvalue')
           if allergens:
               nutrition['allergens'] = allergens.text.strip()
           
           # Get serving containers/portions if available
           servings_div = facts_table.find_all('div', class_='nutfactsservsize')
           if servings_div:
               nutrition['serving_size'] = servings_div[1].text.strip()

           return nutrition
        

async def get_nutrition_urls(menu_html: str) -> List[Dict]:
   """Get nutrition label URLs from menu page."""
   soup = BeautifulSoup(menu_html, 'html.parser')
   items = []
   for dispname in soup.find_all('div', class_='longmenucoldispname'):
       if label_link := dispname.find('a', href=lambda x: x and 'label.aspx' in x):
           station = dispname.find_previous('div', class_='shortmenucats')
           station_name = station.text.strip(' -') if station else 'Unknown'
           items.append({
               'name': label_link.text.strip(),
               'nutrition_url': label_link['href'],
               'station': station_name
           })
   return items

async def parse_food_html(html: str) -> List[Meal]:
   """Parse dining hall menu HTML including nutrition data."""
   menu_urls = await get_menu_urls(html)
   
   meals = []
   async with aiohttp.ClientSession() as session:
       for menu_url in menu_urls:
           async with session.get(f"http://nutritionanalysis.dds.uconn.edu/{menu_url}") as resp:
               menu_html = await resp.text() 
               items = await get_nutrition_urls(menu_html)
               
               stations = {}
               for item in items:
                   nutrition = await get_nutrition_info(
                       "http://nutritionanalysis.dds.uconn.edu", 
                       item['nutrition_url']
                   )
                   if item['station'] not in stations:
                       stations[item['station']] = []
                   stations[item['station']].append({
                       'name': item['name'],
                       'nutrition': nutrition
                   })
               
               meal_name = menu_url.split('mealName=')[-1]
               station_list = [
                   Station(name=capitalize_first(name), options=opts)
                   for name, opts in stations.items() 
                   if name != 'LATE NIGHT'
               ]
               meals.append(Meal(name=meal_name, stations=station_list))
               
               if meal_name == 'Dinner' and 'LATE NIGHT' in stations:
                   meals.append(Meal(
                       name='Late Night',
                       stations=[Station(
                           name='Late Night',
                           options=stations['LATE NIGHT']
                       )]
                   ))
   
   return meals

async def get_menu(hall_type: DiningHallType, date: datetime = None) -> Optional[DiningHallResponse]:
   """Get menu for a dining hall including nutrition info."""
   if date is None:
       date = datetime.now()
   
   hall_key = get_enum_key_by_enum_value(DiningHallType, hall_type)
   hall = DINING_HALLS[hall_key]
   
   url = (
       f"http://nutritionanalysis.dds.uconn.edu/shortmenu.aspx"
       f"?sName=UCONN+Dining+Services"
       f"&locationNum={hall.location.id}"
       f"&locationName={hall.location.name}"
       f"&naFlag=1"
       f"&WeeksMenus=This+Week%27s+Menus"
       f"&myaction=read"
       f"&dtdate={date.strftime('%m')}%2f{date.day}%2f{date.year}"
   )
   
   try:
       async with aiohttp.ClientSession() as session:
           async with session.get(url) as response:
               html = await response.text()
               meals = await parse_food_html(html)
               
               return DiningHallResponse(
                   **vars(hall),
                   time=date,
                   meals=meals,
                   type=get_enum_key_by_enum_value(DiningHallType, hall_type),
                   status=get_dining_hall_status(hall_type, date)
               )
   except Exception as e:
       print(f"Error fetching menu: {e}")
       return None

async def get_dining_json():
   """Get complete dining hall data and convert to JSON."""
   dining_halls = [
       DiningHallType.CONNECTICUT,
       DiningHallType.MCMAHON, 
       DiningHallType.NORTH,
       DiningHallType.NORTHWEST,
       DiningHallType.PUTNAM,
       DiningHallType.SOUTH,
       DiningHallType.TOWERS,
       DiningHallType.WHITNEY
   ]
   
   tasks = [get_menu(hall) for hall in dining_halls]
   results = await asyncio.gather(*tasks)
   
   dining_data = {}
   for result in results:
       if result:
           dining_data[result.name] = {
               'status': result.status,
               'meals': [
                   {
                       'name': meal.name,
                       'stations': [
                           {
                               'name': station.name,
                               'items': [
                                   {
                                       'name': item['name'],
                                       'nutrition': item['nutrition']
                                   } for item in station.options
                               ]
                           } for station in meal.stations
                       ]
                   } for meal in result.meals
               ]
           }
           
   return dining_data

if __name__ == "__main__":
   x = asyncio.run(get_dining_json())
   print(x)