from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

app = FastAPI()


# --- ADD THIS BLOCK ---
# Allow your frontend to talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your frontend's actual URL (e.g., ["http://localhost:3000"])
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
# ----------------------

# Get the directory where api.py is located (the 'server' folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Go up one level to the main project folder (EnergyMap)
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Explicitly point to the db in the project root
DB_PATH = os.path.join(PROJECT_ROOT, "energy_stats.db")

@app.get("/api/energy")
def get_energy(project: str = Query(...)):
    # ... your existing database logic ...
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT module, mean, median, variance, best_case, worst_case 
        FROM module_energy_stats 
        WHERE project = ?
    """, (project,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return {"project": project, "modules": []}
        
    modules = [dict(row) for row in rows]
    
    return {
        "project": project,
        "modules": modules
    }