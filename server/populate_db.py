import sqlite3
import csv
import os

DATABASE = "energy_map.db"
CSV_PATH = "data/module_energy_stats.csv"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create the table using the exact schema provided
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
    
    # Read the CSV and populate the database
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            module_path = row["module"]
            
            # Extract the project name from the path (e.g., ../repos/black/... -> black)
            parts = module_path.split('/')
            if len(parts) > 2 and parts[1] == 'repos':
                project = parts[2]
            else:
                continue
                
            module_name = os.path.basename(module_path)
            
            # Map the CSV package stats to the database columns
            # Variance is the square of the standard deviation
            mean = float(row["package_mean"])
            median = float(row["package_median"])
            stdev = float(row["package_stdev"])
            variance = stdev ** 2  
            best_case = float(row["package_best"])
            worst_case = float(row["package_worst"])
            
            cursor.execute("""
                INSERT OR IGNORE INTO module_energy_stats 
                (project, module, mean, median, variance, best_case, worst_case)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (project, module_name, mean, median, variance, best_case, worst_case))

    conn.commit()
    conn.close()
    print(f"Database {DATABASE} successfully populated from {CSV_PATH}.")

if __name__ == "__main__":
    init_db()