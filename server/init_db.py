import sqlite3
import csv
import os

DB_PATH = "energy_stats.db" # Update this to your actual database file path if it's different
CSV_PATH = "data/module_energy_stats.csv"

def init_db():
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS module_energy_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT NOT NULL,
            module TEXT NOT NULL,
            mean REAL,
            median REAL,
            variance REAL,
            best_case REAL,
            worst_case REAL,
            UNIQUE(project, module)
        );
    """)

    if not os.path.exists(CSV_PATH):
        print(f"Error: Could not find {CSV_PATH}")
        return

    # Read the CSV and insert data
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            module_path = row["module"]
            
            # Extract the project name and the module name from the path
            # Example path: ../repos/black/src/black/output.py
            parts = module_path.split("/")
            if "repos" in parts:
                repo_index = parts.index("repos")
                project = parts[repo_index + 1]
            else:
                continue # Skip if we can't identify the project
                
            module_name = os.path.basename(module_path)
            
            # Extract metrics (mapping from package fields for this example)
            mean = float(row.get("package_mean", 0))
            median = float(row.get("package_median", 0))
            # Variance wasn't explicitly in the example CSV, but we can square the stdev
            stdev = float(row.get("package_stdev", 0))
            variance = stdev ** 2 
            best_case = float(row.get("package_best", 0))
            worst_case = float(row.get("package_worst", 0))

            # Insert or replace to avoid UNIQUE constraint failures if run multiple times
            cursor.execute("""
                INSERT OR REPLACE INTO module_energy_stats 
                (project, module, mean, median, variance, best_case, worst_case)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (project, module_name, mean/1e6, median/1e6, variance/1e6, best_case/1e6, worst_case/1e6))

    conn.commit()
    conn.close()
    print("Database updated successfully!")

if __name__ == "__main__":
    init_db()