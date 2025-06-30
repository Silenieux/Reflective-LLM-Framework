import sqlite3
from pathlib import Path

db_path = Path("memory") / "symbolic_memory.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Rename table safely
cursor.execute("ALTER TABLE symbolic_memory RENAME TO reflective_memory")
conn.commit()

print("✅ Table renamed: symbolic_memory → reflective_memory")
conn.close()
