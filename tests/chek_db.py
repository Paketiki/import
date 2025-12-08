import sys
from pathlib import Path

# Ensure project root is on sys.path so `import app` works when running this script
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import sqlite3

def check_table_structure():
    """Check table structure directly via SQLite (sync)."""
    db_path = ROOT / "test.db"  # adjust if your db file is named differently
    
    if not db_path.exists():
        print(f"Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    for table in ['roles', 'picks', 'users']:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print(f"\nКолонки в таблице '{table}':")
            for col in columns:
                col_id, col_name, col_type, notnull, default, pk = col
                print(f"  - {col_name}: {col_type} (nullable={not notnull})")
        except Exception as e:
            print(f"Ошибка при чтении таблицы '{table}': {e}")
    
    conn.close()

if __name__ == "__main__":
    check_table_structure()