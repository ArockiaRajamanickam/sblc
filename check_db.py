from app.infrastructure.db import engine, settings
from sqlalchemy import text

print(f"Connecting to: {settings.database_url}")
with engine.connect() as conn:
    print("Tables in database:")
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
    for row in result:
        print(f" - {row[0]}")
    
    print("\nChecking 'nodes' table:")
    try:
        count = conn.execute(text("SELECT count(*) FROM nodes")).scalar()
        print(f"Total nodes: {count}")
    except Exception as e:
        print(f"Error checking nodes: {e}")
