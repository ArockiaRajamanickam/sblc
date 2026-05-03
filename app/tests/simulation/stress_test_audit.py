import hashlib
import json
import time
from uuid import uuid4
from decimal import Decimal

def calculate_hash(data, previous_hash):
    payload_str = json.dumps(data, sort_keys=True, default=str)
    content = f"{payload_str}|{previous_hash}"
    return hashlib.sha256(content.encode()).hexdigest()

def simulate_audit_chain(count=1000):
    print(f"Generating {count} hash-chained audit logs...")
    chain = []
    previous_hash = "0" * 64
    
    start_time = time.time()
    for i in range(count):
        payload = {
            "event": "transaction.created",
            "amount": float(Decimal("1000.00") * i),
            "user": str(uuid4())
        }
        current_hash = calculate_hash(payload, previous_hash)
        chain.append({
            "payload": payload,
            "previous_hash": previous_hash,
            "current_hash": current_hash
        })
        previous_hash = current_hash
    
    end_time = time.time()
    print(f"Generated {count} logs in {end_time - start_time:.4f} seconds.")
    
    # Verification
    print("Verifying chain integrity...")
    for i in range(1, len(chain)):
        expected_hash = calculate_hash(chain[i]["payload"], chain[i-1]["current_hash"])
        if expected_hash != chain[i]["current_hash"]:
            print(f"INTEGRITY BREAK AT INDEX {i}")
            return False
    
    print("Chain integrity verified successfully.")
    return True

if __name__ == "__main__":
    simulate_audit_chain(10000)
    # Tamper test
    print("\nSimulating tampering...")
    # Change any payload in the middle
    # ...
