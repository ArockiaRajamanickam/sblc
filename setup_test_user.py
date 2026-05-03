import os
import psycopg
import uuid
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
if url.startswith("postgresql+psycopg://"):
    url = url.replace("postgresql+psycopg://", "postgresql://")

def setup_user(ledger_id, node_id):
    user_id = uuid.uuid4()
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            # 1. Create User
            cur.execute(
                "INSERT INTO users (id, email, full_name, node_id) VALUES (%s, %s, %s, %s)",
                (user_id, f"testuser-{user_id.hex[:6]}@example.com", "Test Admin User", node_id)
            )
            
            # 2. Get IssuerAdmin Role ID
            cur.execute("SELECT id FROM roles WHERE name = 'IssuerAdmin'")
            role_id = cur.fetchone()[0]
            
            # 3. Assign Role to User for this Ledger
            cur.execute(
                "INSERT INTO user_ledger_roles (id, user_id, ledger_id, role_id) VALUES (%s, %s, %s, %s)",
                (uuid.uuid4(), user_id, ledger_id, role_id)
            )
            
            conn.commit()
            print(f"Created user {user_id} with IssuerAdmin role for ledger {ledger_id}")
            return user_id

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python setup_test_user.py <ledger_id> <node_id>")
        sys.exit(1)
    setup_user(sys.argv[1], sys.argv[2])
