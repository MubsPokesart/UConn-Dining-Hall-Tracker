import json
import asyncio
from dining_hall_handler import get_dining_json


def analyze_protein_content(data, min_protein=15):
    """Find items with high protein content across dining halls by meal."""
    high_protein_items = {}
    
    for dining_hall, hall_data in data.items():
        if dining_hall in ['status', 'meals']: continue  # Skip non-dining hall keys
        
        # Create entry for this dining hall if it doesn't exist
        if dining_hall not in high_protein_items:
            high_protein_items[dining_hall] = {}
        
        # Process each meal separately
        for meal in hall_data.get('meals', []):
            meal_name = meal.get('name', 'Unknown')
            items_list = []
            
            for station in meal.get('stations', []):
                for item in station.get('items', []):
                    protein_str = item.get('nutrition', {}).get('protein', '0')
                    try:
                        # Convert protein string to float (remove 'g' if present)
                        protein = float(protein_str.rstrip('g'))
                        if protein >= min_protein:
                            items_list.append({
                                'name': item['name'],
                                'protein': protein,
                                'calories': float(item.get('nutrition', {}).get('calories', 0)),
                                'station': station.get('name', 'Unknown')
                            })
                    except (ValueError, TypeError):
                        continue
            
            if items_list:
                # Sort by protein content
                items_list.sort(key=lambda x: x['protein'], reverse=True)
                high_protein_items[dining_hall][meal_name] = items_list
    
    return high_protein_items

def analyze_protein_ratio(data, min_ratio=5):
    """Find items with high protein-to-calorie ratios across dining halls by meal."""
    high_protein_ratio_items = {}
    
    for dining_hall, hall_data in data.items():
        if dining_hall in ['status', 'meals']: continue
        
        # Create entry for this dining hall if it doesn't exist
        if dining_hall not in high_protein_ratio_items:
            high_protein_ratio_items[dining_hall] = {}
        
        # Process each meal separately
        for meal in hall_data.get('meals', []):
            meal_name = meal.get('name', 'Unknown')
            items_list = []
            
            for station in meal.get('stations', []):
                for item in station.get('items', []):
                    try:
                        protein = float(item.get('nutrition', {}).get('protein', '0').rstrip('g'))
                        calories = float(item.get('nutrition', {}).get('calories', 0))
                        
                        if calories > 0 and protein > 0:
                            ratio = (protein / calories) * 100  # Protein per 100 calories
                            if ratio >= min_ratio:
                                items_list.append({
                                    'name': item['name'],
                                    'protein': protein,
                                    'calories': calories,
                                    'ratio': ratio,
                                    'station': station.get('name', 'Unknown')
                                })
                    except (ValueError, TypeError, ZeroDivisionError):
                        continue
            
            if items_list:
                # Sort by protein ratio
                items_list.sort(key=lambda x: x['ratio'], reverse=True)
                high_protein_ratio_items[dining_hall][meal_name] = items_list[:5]  # Top 5 items per meal
    
    return high_protein_ratio_items

async def main():
    data = await get_dining_json()
    
    data_json = json.dumps(data, indent=4)

    with open('data.json', 'w') as f:
        f.write(data_json)

async def protein():
    data = await get_dining_json()
    protein_ratio_items = analyze_protein_ratio(data)
    
    # Print results organized by dining hall and meal
    for dining_hall, meals in protein_ratio_items.items():
        print(f"\n=== {dining_hall} ===")
        
        for meal_name, items in meals.items():
            print(f"\n  ** {meal_name} **")
            
            if not items:
                print("    No high-protein items found")
                continue
                
            for item in items:
                print(f"    {item['name']} ({item['station']}): {item['ratio']:.2f}g protein per 100 calories")
                print(f"      {item['protein']}g protein, {item['calories']} calories")


if __name__ == "__main__":
    asyncio.run(protein())