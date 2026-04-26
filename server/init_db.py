import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "energy_stats.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS module_energy_stats;")
    cursor.execute("DROP TABLE IF EXISTS module_energy_hierarchy;")

    cursor.execute("""
        CREATE TABLE module_energy_hierarchy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT NOT NULL,
            module TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('internal', 'stdlib', 'external')),
            parent_module TEXT,
            energy REAL NOT NULL,
            view TEXT NOT NULL CHECK(view IN ('nested', 'flat')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(repo, module, category, parent_module, view)
        );
    """)

    cursor.execute("CREATE INDEX idx_repo_view ON module_energy_hierarchy(repo, view);")
    cursor.execute("CREATE INDEX idx_parent_module ON module_energy_hierarchy(parent_module);")

    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {DB_PATH}!")

if __name__ == "__main__":
    init_db()