# Blueplate

![version badge](https://img.shields.io/badge/version-1.1.0-blue)

Blueplate is a TypeScript library that allows you to easily fetch menus for UConn Dining Halls.

## Installation

Use npm to install Blueplate.

```bash
npm install @ilefa/blueplate
```

## Usage

```ts
import { getMenu, DiningHallType } from '@ilefa/bluepages';

// Fetch meals being served at South
let meals = await getMenu(DiningHallType.SOUTH);

{
   "name": "South",
   "lateNight": false,
   "status": "LUNCH",
   "location": {
      "id": "16",
      "name": "South+Campus+Marketplace",
      "latitude": 41.803892,
      "longitude": -72.248538
   },
   "meals": [
      {
         "name": "Breakfast",
         "stations": [
            {
               "name": "Breakfast Entrees",
               "options": [
                  "Cheesy Scrambled Eggs",
                  "Hard Boiled Eggs",
                  "Mini Potato Pancakes",
                  "Oatmeal Hot Cereal",
                  "Plant-Based Breakfast Sausage",
                  "Sausage Patties",
                  "Scrambled Eggs",
                  "Vegan French Toast"
               ]
            },
            {
               "name": "Breakfast Bakery",
               "options": [
                  "Strawberry crunch donut"
               ]
            },
            {
               "name": "Grill Station",
               "options": [
                  "Chefs Omelet Du Jour"
               ]
            }
         ]
      },
      {
         "name": "Lunch",
         "stations": [
            {
               "name": "Smart Check Entrees",
               "options": [
                  "Grilled Chicken Breast"
               ]
            },
            {
               "name": "Soups",
               "options": [
                  "Chef's Choice Soup du Jour"
               ]
            },
            {
               "name": "Grill Items",
               "options": [
                  "Awesome Burger",
                  "Beef Burger No Bun",
                  "Cross Trax French Fries",
                  "Grilled Cheese",
                  "Grilled Hot Dogs"
               ]
            },
            {
               "name": "Halal",
               "options": [
                  "Halal Chicken Fajita"
               ]
            },
            {
               "name": "Comfort Line",
               "options": [
                  "Bacon Cheddar Mashed Potatoes",
                  "Corn Cobetts",
                  "Fried Chicken Nuggets",
                  "Panko Crusted Scrod Filet",
                  "Rice Florentine",
                  "Sliced Carrots"
               ]
            },
            {
               "name": "International Station",
               "options": [
                  "Char Siu Pork Chops",
                  "Sesame Broccoli"
               ]
            },
            {
               "name": "Options",
               "options": [
                  "Garlic Bread with Cheese",
                  "Marinara Sauce"
               ]
            },
            {
               "name": "Desserts",
               "options": [
                  "Chocolate Brownies",
                  "Jonathan Bar"
               ]
            }
         ]
      },
      {
         "name": "Dinner",
         "stations": [
            {
               "name": "Smart Check Entrees",
               "options": [
                  "Grilled Chicken Breast"
               ]
            },
            {
               "name": "Soups",
               "options": [
                  "Chef's Choice Soup du Jour"
               ]
            },
            {
               "name": "Grill Items",
               "options": [
                  "Awesome Burger",
                  "Beef Burger No Bun",
                  "Cross Trax French Fries",
                  "Grilled Cheese",
                  "Grilled Hot Dogs"
               ]
            },
            {
               "name": "Halal",
               "options": [
                  "Halal Spaghetti & Meatballs"
               ]
            },
            {
               "name": "Comfort Line",
               "options": [
                  "Indian Bar"
               ]
            },
            {
               "name": "International Station",
               "options": [
                  "Boneless Chinese BBQ Pork",
                  "Broccoli Stir Fry w/ Ginger",
                  "Sesame Noodles",
                  "White Rice"
               ]
            },
            {
               "name": "Options",
               "options": [
                  "Cajun Salmon W/ Honey Dill Mustard Sauce",
                  "Garden Blend Rice",
                  "Vegetable Samosas w/ Chutney"
               ]
            },
            {
               "name": "Desserts",
               "options": [
                  "Apple Pie"
               ]
            }
         ]
      }
   ]
}
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)