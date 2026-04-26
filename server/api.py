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

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

@app.get("/api/energy/nested")
def get_energy_nested(repo: str = Query(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get top-level internal modules
    cursor.execute("""
        SELECT module, category, energy 
        FROM module_energy_hierarchy 
        WHERE repo = ? AND view = 'nested' AND parent_module IS NULL
    """, (repo,))
    
    top_level_rows = cursor.fetchall()
    
    modules = []
    for row in top_level_rows:
        module_name = row["module"]
        module_data = {
            "module": module_name,
            "category": row["category"],
            "energy": row["energy"],
            "dependencies": []
        }
        
        # Get dependencies for this module
        cursor.execute("""
            SELECT module, category, energy 
            FROM module_energy_hierarchy 
            WHERE repo = ? AND view = 'nested' AND parent_module = ?
        """, (repo, module_name))
        
        dep_rows = cursor.fetchall()
        for dep in dep_rows:
            module_data["dependencies"].append({
                "module": dep["module"],
                "category": dep["category"],
                "energy": dep["energy"]
            })
            
        modules.append(module_data)
        
    conn.close()
    
    return {
        "repo": repo,
        "view": "nested",
        "modules": modules
    }

@app.get("/api/energy/flat")
def get_energy_flat(repo: str = Query(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT module, category, energy 
        FROM module_energy_hierarchy 
        WHERE repo = ? AND view = 'flat'
    """, (repo,))
    
    rows = cursor.fetchall()
    conn.close()
    
    internal = []
    stdlib = []
    external = []
    
    for row in rows:
        item = {"module": row["module"], "energy": row["energy"]}
        if row["category"] == "internal":
            internal.append(item)
        elif row["category"] == "stdlib":
            stdlib.append(item)
        elif row["category"] == "external":
            external.append(item)
            
    return {
        "repo": repo,
        "view": "flat",
        "internal": internal,
        "stdlib": stdlib,
        "external": external
    }

@app.get("/api/repositories")
def get_repositories():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT repo FROM module_energy_hierarchy")
    rows = cursor.fetchall()
    conn.close()
    
    repos = [row["repo"] for row in rows]
    
    return {"repositories": repos}