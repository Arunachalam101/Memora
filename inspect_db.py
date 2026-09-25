import sqlite3

conn = sqlite3.connect('data/memora.sqlite')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("="*70)
print("DATABASE INSPECTION - MEMORA.SQLITE")
print("="*70)

if not tables:
    print("NO TABLES FOUND")
else:
    for table in tables:
        table_name = table[0]
        print(f"\n{table_name}:")
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print("  Columns:")
        for col in columns:
            print(f"    - {col[1]} ({col[2]})")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Rows: {count}")
        
        # Show sample data if exists
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            print(f"  Sample data (first 3):")
            for row in rows:
                print(f"    {row}")

conn.close()
print("\n" + "="*70)
