import sqlite3

conn = sqlite3.connect("quiz.db")
c = conn.cursor()

# Check existing columns
existing = [row[1] for row in c.execute("PRAGMA table_info(scores)").fetchall()]
print("Existing columns:", existing)

# Add missing columns
migrations = [
    ("category",        "TEXT DEFAULT 'gk'"),
    ("difficulty",      "TEXT DEFAULT 'medium'"),
    ("total_questions", "INTEGER DEFAULT 3"),
    ("time_taken",      "INTEGER DEFAULT 0"),
    ("date",            "TEXT"),
]

for col_name, col_def in migrations:
    if col_name not in existing:
        c.execute(f"ALTER TABLE scores ADD COLUMN {col_name} {col_def}")
        print(f"Added column: {col_name}")
    else:
        print(f"Column already exists: {col_name}")

conn.commit()

# Verify final schema
c.execute("PRAGMA table_info(scores)")
print("Final columns:", [row[1] for row in c.fetchall()])

# Show all rows
c.execute("SELECT * FROM scores")
rows = c.fetchall()
print(f"Total rows: {len(rows)}")
for row in rows:
    print(" ", row)

conn.close()
print("Migration complete!")
