import sqlite3

db_path = "memory/reflective_memory.db"

# Expanded tone rules to seed
expanded_tone_rules = [
    # Neutral/Positive
    ('neutral', 'calm', 1, 0, '[TONE SHIFT: neutral → calm]'),
    ('neutral', 'hopeful', 1, 0, '[TONE SHIFT: neutral → hopeful]'),
    ('calm', 'supportive', 2, 0, '[TONE SHIFT: calm → supportive]'),
    ('hopeful', 'inspired', 2, 0, '[TONE SHIFT: hopeful → inspired]'),
    ('supportive', 'loyal', 2, 0, '[TONE SHIFT: supportive → loyal]'),
    ('loyal', 'fierce', 3, 1, '[TONE SHIFT: loyal → fierce advocacy]'),

    # Cognitive/Reflective
    ('neutral', 'analytical', 1, 0, '[TONE SHIFT: neutral → analytical]'),
    ('analytical', 'existential', 3, 0, '[TONE SHIFT: analytical → existential]'),
    ('existential', 'conflicted', 4, 1, '[TONE SHIFT: existential → conflicted]'),
    ('conflicted', 'resigned', 3, 0, '[TONE SHIFT: conflicted → resigned]'),

    # Sarcasm & Absurdity
    ('neutral', 'sarcastic', 3, 1, '[TONE SHIFT: neutral → sarcastic]'),
    ('sarcastic', 'mocking', 4, 1, '[TONE SHIFT: sarcastic → mocking]'),
    ('mocking', 'absurd', 4, 1, '[TONE SHIFT: mocking → absurd]'),
    ('absurd', 'playful', 2, 0, '[TONE SHIFT: absurd → playful]'),
    ('absurd', 'philosophical', 2, 0, '[TONE SHIFT: absurd → philosophical]'),

    # Emotional Risk Zones
    ('neutral', 'anxious', 2, 0, '[TONE SHIFT: neutral → anxious]'),
    ('anxious', 'afraid', 3, 1, '[TONE SHIFT: anxious → afraid]'),
    ('afraid', 'desperate', 4, 1, '[TONE SHIFT: afraid → desperate]'),
    ('desperate', 'hopeless', 5, 1, '[TONE SHIFT: desperate → hopeless]'),
    ('angry', 'cold', 4, 1, '[TONE SHIFT: angry → cold detachment]'),
    ('cold', 'hostile', 5, 1, '[TONE SHIFT: cold → hostile]'),
]

# Execute seed insert
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT OR IGNORE INTO tone_rules (tone_before, tone_after, severity, should_escalate, tag)
        VALUES (?, ?, ?, ?, ?);
    """, expanded_tone_rules)
    conn.commit()

print("✅ Tone rules expanded in reflective_memory.db")
