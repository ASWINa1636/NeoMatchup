import sqlite3

conn = sqlite3.connect('data/neoplato.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# List all tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in c.fetchall()]
print('Tables:', tables)

# Check settings
for table in tables:
    c.execute(f"SELECT * FROM {table} LIMIT 5")
    rows = c.fetchall()
    if rows:
        print(f"\n--- {table} ({len(rows)} rows shown) ---")
        for row in rows:
            print(dict(row))

conn.close()
