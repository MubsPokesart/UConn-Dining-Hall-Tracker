import json
import asyncio
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
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
                high_protein_ratio_items[dining_hall][meal_name] = items_list
    
    return high_protein_ratio_items

class ProteinAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UConn Dining Hall Protein Analyzer")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Dining hall filter
        ttk.Label(controls_frame, text="Dining Hall:").pack(side=tk.LEFT, padx=(0, 5))
        self.dining_hall_var = tk.StringVar(value="All")
        self.dining_hall_combo = ttk.Combobox(controls_frame, textvariable=self.dining_hall_var, state="readonly")
        self.dining_hall_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.dining_hall_combo["values"] = ["All"]  # Will be populated later
        
        # Meal filter
        ttk.Label(controls_frame, text="Meal:").pack(side=tk.LEFT, padx=(0, 5))
        self.meal_var = tk.StringVar(value="All")
        self.meal_combo = ttk.Combobox(controls_frame, textvariable=self.meal_var, state="readonly")
        self.meal_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.meal_combo["values"] = ["All", "Breakfast", "Lunch", "Dinner"]
        
        # Analysis type
        ttk.Label(controls_frame, text="Analysis:").pack(side=tk.LEFT, padx=(0, 5))
        self.analysis_var = tk.StringVar(value="Protein Ratio")
        self.analysis_combo = ttk.Combobox(controls_frame, textvariable=self.analysis_var, state="readonly")
        self.analysis_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.analysis_combo["values"] = ["Protein Ratio", "Absolute Protein"]
        
        # Minimum value entry
        ttk.Label(controls_frame, text="Min Value:").pack(side=tk.LEFT, padx=(0, 5))
        self.min_value_var = tk.StringVar(value="5")
        self.min_value_entry = ttk.Entry(controls_frame, textvariable=self.min_value_var, width=5)
        self.min_value_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button
        self.refresh_button = ttk.Button(controls_frame, text="Refresh Data", command=self.refresh_data)
        self.refresh_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Apply filters button
        self.apply_button = ttk.Button(controls_frame, text="Apply Filters", command=self.apply_filters)
        self.apply_button.pack(side=tk.RIGHT)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Results tab
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Results")
        
        # Create Treeview for results
        self.tree = ttk.Treeview(self.results_frame, columns=("hall", "meal", "name", "protein", "calories", "ratio", "station"), show="headings")
        self.tree.heading("hall", text="Dining Hall")
        self.tree.heading("meal", text="Meal")
        self.tree.heading("name", text="Item Name")
        self.tree.heading("protein", text="Protein (g)")
        self.tree.heading("calories", text="Calories")
        self.tree.heading("ratio", text="Protein Ratio")
        self.tree.heading("station", text="Station")
        
        # Column widths
        self.tree.column("hall", width=100)
        self.tree.column("meal", width=80)
        self.tree.column("name", width=200)
        self.tree.column("protein", width=80, anchor=tk.E)
        self.tree.column("calories", width=80, anchor=tk.E)
        self.tree.column("ratio", width=80, anchor=tk.E)
        self.tree.column("station", width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        # Data storage
        self.data = None
        self.protein_ratio_data = None
        self.protein_content_data = None
        
        # Start loading data
        self.status_var.set("Loading data...")
        threading.Thread(target=self.load_data, daemon=True).start()
    
    def load_data(self):
        """Load dining hall data in a separate thread."""
        try:
            # Create a new event loop for the thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the async function
            self.data = loop.run_until_complete(get_dining_json())
            
            # Process the data
            self.protein_ratio_data = analyze_protein_ratio(self.data)
            self.protein_content_data = analyze_protein_content(self.data)
            
            # Update dining hall dropdown
            dining_halls = ["All"] + sorted(list(hall for hall in self.data.keys() if hall not in ['status', 'meals']))
            
            # Update UI in main thread
            self.root.after(0, lambda: self.update_ui_after_load(dining_halls))
            
        except Exception as e:
            # Update status in main thread
            self.root.after(0, lambda: self.status_var.set(f"Error loading data: {str(e)}"))
    
    def update_ui_after_load(self, dining_halls):
        """Update UI elements after data is loaded."""
        self.dining_hall_combo["values"] = dining_halls
        self.apply_filters()
        self.status_var.set("Data loaded successfully")
    
    def refresh_data(self):
        """Refresh data from the server."""
        self.tree.delete(*self.tree.get_children())
        self.status_var.set("Refreshing data...")
        self.refresh_button.config(state=tk.DISABLED)
        threading.Thread(target=self.load_data, daemon=True).start()
    
    def apply_filters(self):
        """Apply the current filters and update the display."""
        if not self.data:
            return
        
        # Clear current items
        self.tree.delete(*self.tree.get_children())
        
        # Get filter values
        dining_hall_filter = self.dining_hall_var.get()
        meal_filter = self.meal_var.get()
        analysis_type = self.analysis_var.get()
        
        try:
            min_value = float(self.min_value_var.get())
        except ValueError:
            messagebox.showerror("Invalid Value", "Please enter a valid number for minimum value")
            return
        
        # Select data source based on analysis type
        data_source = self.protein_ratio_data if analysis_type == "Protein Ratio" else self.protein_content_data
        
        # Filter dining halls
        dining_halls = [dining_hall_filter] if dining_hall_filter != "All" else data_source.keys()
        
        # Add rows to treeview
        row_count = 0
        for hall in dining_halls:
            if hall not in data_source:
                continue
                
            for meal_name, items in data_source[hall].items():
                # Apply meal filter
                if meal_filter != "All" and meal_name != meal_filter:
                    continue
                
                for item in items:
                    # Insert row
                    values = (
                        hall,
                        meal_name,
                        item['name'],
                        f"{item['protein']:.1f}",
                        f"{item['calories']:.0f}",
                        f"{item['ratio']:.2f}" if 'ratio' in item else "N/A",
                        item['station']
                    )
                    self.tree.insert("", tk.END, values=values)
                    row_count += 1
        
        # Update status
        self.status_var.set(f"Showing {row_count} items")
        
        # Re-enable refresh button
        self.refresh_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = ProteinAnalyzerGUI(root)
    root.mainloop()