import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
if not url:
    print("DATABASE_URL not found in .env")
    exit(1)

# SQLAlchemy URL to psycopg connection string
if url.startswith("postgresql+psycopg://"):
    url = url.replace("postgresql+psycopg://", "postgresql://")

try:
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            # Check for types in all schemas
            cur.execute("""
                SELECT n.nspname, t.typname 
                FROM pg_type t 
                JOIN pg_namespace n ON n.oid = t.typnamespace 
                WHERE t.typname IN ('node_type', 'membership_status')
                AND n.nspname NOT IN ('pg_catalog', 'information_schema');
            """)
            types = cur.fetchall()
            print(f"Existing types across schemas: {types}")
            
            # Drop them if they exist
            for schema, name in types:
                print(f"Dropping type {schema}.{name}")
                cur.execute(f'DROP TYPE IF EXISTS "{schema}"."{name}" CASCADE;')
            conn.commit()
            print("Successfully dropped types.")
            
            # Check for tables
            cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public';")
            tables = cur.fetchall()
            print(f"Existing tables: {tables}")
            
            # If alembic_version exists, check it
            cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public' AND tablename = 'alembic_version';")
            if cur.fetchone():
                cur.execute("SELECT version_num FROM alembic_version;")
                version = cur.fetchone()
                print(f"Alembic version: {version}")
except Exception as e:
    print(f"Error: {e}")
