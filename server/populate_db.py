import sqlite3
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "energy_stats.db")
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "module_energy_stats.csv")

def populate_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Try multiple common paths for the new aggregation output CSV
    possible_paths = [
        CSV_PATH
    ]
    
    csv_file_to_use = None
    for p in possible_paths:
        if os.path.exists(p):
            csv_file_to_use = p
            break
            
    if not csv_file_to_use:
        print("Error: Could not find the new aggregation output CSV file.")
        print(f"Looked in: {possible_paths}")
        return

    with open(csv_file_to_use, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            repo = row["repo"]
            module = row["module"]
            category = row["category"]
            parent_module = row["parent_module"] if row.get("parent_module") else None
            energy = float(row["energy"])
            view = row["view"]
            
            cursor.execute("""
                INSERT OR REPLACE INTO module_energy_hierarchy 
                (repo, module, category, parent_module, energy, view)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (repo, module, category, parent_module, energy, view))

    conn.commit()
    conn.close()
    print(f"Database {DB_PATH} successfully populated from {csv_file_to_use}.")

if __name__ == "__main__":
    populate_db()