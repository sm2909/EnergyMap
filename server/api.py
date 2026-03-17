from fastapi import FastAPI, HTTPException, Depends
import sqlite3
from typing import List, Dict, Any
import statistics

# ==========================================
# 1. APPLICATION INITIALIZATION
# ==========================================
# FastAPI() creates our main application instance. 
# This `app` object handles routing our endpoints (GET, POST, etc.)
app = FastAPI(
    title="EnergyMap API",
    description="API endpoints for exposing backend energy statistics data.",
)

# Replace 'energy_map.db' with your actual database file path
DATABASE = "energy_map.db"

# ==========================================
# 2. DATABASE DEPENDENCY
# ==========================================
# In FastAPI, "Dependencies" are functions that run before your endpoint logic.
# They are perfect for opening a database connection and closing it afterward.
def get_db_connection():
    # `sqlite3.connect` opens the file.
    conn = sqlite3.connect(DATABASE)
    # `sqlite3.Row` lets us access columns by name (e.g., row['module_name'])
    # instead of by index (e.g., row[0]).
    conn.row_factory = sqlite3.Row
    try:
        # `yield` pauses this function and passes the connection to the endpoint.
        yield conn
    finally:
        # Once the endpoint finishes, the function resumes here and closes the connection.
        conn.close()


# ==========================================
# 3. GET PROJECT MODULES ENDPOINT
# ==========================================
# @app.get() is a "decorator". It tells FastAPI that this function handles 
# HTTP GET requests to the specified URL path.
# `{project}` is a path parameter. It will be passed as an argument to the function.
@app.get("/projects/{project}/modules", response_model=List[str])
def get_project_modules(project: str, db: sqlite3.Connection = Depends(get_db_connection)):
    """
    Returns a list of modules associated with a specific project.
    """
    # 📝 SQL Syntax Explanation:
    # `SELECT DISTINCT` ensures we only get unique module names.
    # The `?` is a placeholder to prevent SQL injection.
    query = "SELECT DISTINCT module_name FROM modules WHERE project_name = ?"
    
    # Execute the query and pass the `project` variable into the placeholder.
    cursor = db.execute(query, (project,))
    rows = cursor.fetchall()
    
    if not rows:
        # HTTPException stops the function and returns an error code to the frontend.
        raise HTTPException(status_code=404, detail="Project not found or no modules available.")
        
    # Return a simple list of strings. FastAPI automatically converts this to JSON.
    return [row["module_name"] for row in rows]


# ==========================================
# 4. GET MODULE ENERGY STATS ENDPOINT
# ==========================================
@app.get("/projects/{project}/module-energy", response_model=Dict[str, Any])
def get_module_energy_stats(project: str, db: sqlite3.Connection = Depends(get_db_connection)):
    """
    Returns statistics: mean, median, variance, best/worst case.
    """
    query = """
        SELECT module_name, energy_value 
        FROM testcases 
        WHERE project_name = ?
    """
    cursor = db.execute(query, (project,))
    rows = cursor.fetchall()
    
    if not rows:
        raise HTTPException(status_code=404, detail="No energy data found for this project.")
    
    # Group energy values by module
    from collections import defaultdict
    module_data = defaultdict(list)
    
    # Loop over database rows to group them
    for row in rows:
        module_name = row["module_name"]
        energy = row["energy_value"]
        module_data[module_name].append(energy)
        
    stats_result = {}
    
    # 📝 Python Syntax Explanation for Stats:
    # We loop through our grouped data. For each module, we calculate its stats
    # using Python's built-in `statistics` module.
    for module, values in module_data.items():
        if not values:
            continue
            
        stats_result[module] = {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "variance": statistics.variance(values) if len(values) > 1 else 0.0,
            # min() and max() are built-in Python functions to find smallest/largest items
            "best_case": min(values),   
            "worst_case": max(values),  
            "count": len(values)
        }
        
    # FastAPI converts this dictionary into a JSON object automatically
    return stats_result


# ==========================================
# 5. GET RAW TESTCASE DATA ENDPOINT
# ==========================================
@app.get("/projects/{project}/testcases", response_model=List[Dict[str, Any]])
def get_raw_testcases(project: str, db: sqlite3.Connection = Depends(get_db_connection)):
    """
    Returns raw testcase data.
    """
    query = """
        SELECT id, module_name, testcase_name, energy_value, timestamp 
        FROM testcases 
        WHERE project_name = ?
    """
    cursor = db.execute(query, (project,))
    rows = cursor.fetchall()
    
    if not rows:
        raise HTTPException(status_code=404, detail="No testcases found for this project.")
        
    # 📝 Syntax Explanation: 
    # `dict(row)` converts the sqlite3.Row object into a standard Python dictionary.
    # The list comprehension `[dict(row) for row in rows]` creates a list of these dictionaries.
    return [dict(row) for row in rows]