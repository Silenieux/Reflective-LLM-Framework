# sqlite_store.py
import sqlite3
import numpy as np
import json
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "./db/symbolic_memory.db")

def init_db(db_path=DB_PATH):
    """Create the database and memory table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        summary TEXT,
        reflective_prompt TEXT,
        bias_tags TEXT,
        memory_type TEXT,
        continuity_cue TEXT,
        reflection_status TEXT,
        tone_context TEXT,
        embedding BLOB,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_memory(entry, embedding, db_path=DB_PATH):
    """Insert a memory reflection and its embedding into the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Convert Python objects to JSON and NumPy to bytes
    tags = json.dumps(entry.get("Bias Tags", []))
    tone = json.dumps(entry.get("tone_context", {}))
    embed_bytes = embedding.astype(np.float32).tobytes()

    cursor.execute("""
    INSERT INTO memory (
        title, summary, reflective_prompt, bias_tags,
        memory_type, continuity_cue, reflection_status,
        tone_context, embedding, timestamp
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry.get("Title", ""),
        entry.get("Summary", ""),
        entry.get("Reflective Prompt", ""),
        tags,
        entry.get("Memory Type", ""),
        entry.get("Continuity Cue", ""),
        entry.get("Reflection Status", ""),
        tone,
        embed_bytes,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

def fetch_all_entries(db_path=DB_PATH):
    """Fetch all memory rows with embedding for comparison."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, summary, reflective_prompt, bias_tags, memory_type, continuity_cue, reflection_status, tone_context, embedding FROM memory")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        entry = {
            "id": row[0],
            "Title": row[1],
            "Summary": row[2],
            "Reflective Prompt": row[3],
            "Bias Tags": json.loads(row[4]),
            "Memory Type": row[5],
            "Continuity Cue": row[6],
            "Reflection Status": row[7],
            "tone_context": json.loads(row[8])
        }
        embedding = np.frombuffer(row[9], dtype=np.float32)
        results.append((entry, embedding))
    return results
