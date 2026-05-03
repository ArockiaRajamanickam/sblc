import requests
import uuid
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

def test_sblc_workflow():
    # 1. Setup test data via direct DB access or Admin API
    # For now, let's assume we use the API to create what we need
    
    # Create a Ledger
    l_resp = requests.post(f"{BASE_URL}/ledgers", json={"name": f"Test Ledger {uuid.uuid4().hex[:6]}", "description": "Verification ledger"})
    l_resp.raise_for_status()
    ledger = l_resp.json()
    ledger_id = ledger["id"]
    print(f"Created Ledger: {ledger_id}")

    # Create Nodes
    issuer_resp = requests.post(f"{BASE_URL}/nodes", json={"legal_name": "Issuer Bank", "node_type": "issuer_bank"})
    issuer_resp.raise_for_status()
    issuer_node = issuer_resp.json()
    print(f"Created Issuer Node: {issuer_node['id']}")
    
    applicant_resp = requests.post(f"{BASE_URL}/nodes", json={"legal_name": "Applicant Corp", "node_type": "applicant"})
    applicant_resp.raise_for_status()
    applicant_node = applicant_resp.json()
    
    beneficiary_resp = requests.post(f"{BASE_URL}/nodes", json={"legal_name": "Beneficiary Ltd", "node_type": "beneficiary"})
    beneficiary_resp.raise_for_status()
    beneficiary_node = beneficiary_resp.json()

    # Get Roles
    roles_resp = requests.get(f"{BASE_URL}/roles")
    roles = {r["name"]: r["id"] for r in roles_resp.json()}
    
    # We need a user. The current schema doesn't have a POST /users, but it has it in models.
    # Let's create a user and assign role via a script or if there's an endpoint.
    # I'll use a small python snippet to create a test user in DB.
    
    print("Please ensure the FastAPI server is running for this test.")
    
    # Normally I'd create a user here, but I'll do it in a separate setup script if needed.
    # For this verification, I'll demonstrate the RBAC by attempting a request without a valid actor.
    
    sblc_payload = {
        "issuing_node_id": issuer_node["id"],
        "applicant_node_id": applicant_node["id"],
        "beneficiary_node_id": beneficiary_node["id"],
        "reference_number": f"REF-{uuid.uuid4().hex[:8].upper()}",
        "amount": 100000.0,
        "currency": "USD",
        "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
        "metadata_json": {"terms": "Standard SBLC terms"}
    }
    
    headers = {"X-Actor-ID": str(uuid.uuid4())} # Random user should fail
    
    print("\nAttempting to create SBLC with unauthorized user...")
    resp = requests.post(f"{BASE_URL}/ledgers/{ledger_id}/sblcs", json=sblc_payload, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Detail: {resp.json().get('detail')}")
    
    if resp.status_code == 403:
        print("✅ RBAC correctly denied unauthorized user.")
    else:
        print("❌ RBAC failed to deny unauthorized user.")

    # 2. Setup user with DB script (we'll call the function directly if imported)
    print("\nSetting up authorized user...")
    from setup_test_user import setup_user
    user_id = setup_user(ledger_id, issuer_node["id"])
    
    headers = {"X-Actor-ID": str(user_id)}
    
    print("\nAttempting to create SBLC with authorized user...")
    resp = requests.post(f"{BASE_URL}/ledgers/{ledger_id}/sblcs", json=sblc_payload, headers=headers)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        sblc = resp.json()
        print(f"✅ SBLC created successfully: {sblc['id']}")
        
        # Test Listing
        print("\nListing SBLCs for ledger...")
        list_resp = requests.get(f"{BASE_URL}/ledgers/{ledger_id}/sblcs", headers=headers)
        print(f"Status: {list_resp.status_code}")
        if list_resp.status_code == 200 and len(list_resp.json()) > 0:
            print(f"✅ Listed {len(list_resp.json())} SBLCs.")
        else:
            print("❌ Failed to list SBLCs.")
            
        # Test Detail
        sblc_id = sblc["id"]
        print(f"\nRetrieving SBLC detail for {sblc_id}...")
        detail_resp = requests.get(f"{BASE_URL}/ledgers/{ledger_id}/sblcs/{sblc_id}", headers=headers)
        print(f"Status: {detail_resp.status_code}")
        if detail_resp.status_code == 200:
            print(f"✅ Retrieved SBLC: {detail_resp.json()['reference_number']}")
        else:
            print("❌ Failed to retrieve SBLC detail.")

        # Phase 2: Transitions
        print("\n--- Phase 2: Transitions ---")
        print(f"Publishing SBLC...")
        pub_resp = requests.post(f"{BASE_URL}/ledgers/{ledger_id}/sblcs/{sblc_id}/publish", headers=headers)
        print(f"Status: {pub_resp.status_code}")
        if pub_resp.status_code == 200:
            print("✅ SBLC Published")
        
        print(f"Issuing SBLC...")
        iss_resp = requests.post(f"{BASE_URL}/ledgers/{ledger_id}/sblcs/{sblc_id}/issue", headers=headers)
        if iss_resp.status_code == 200:
            print("✅ SBLC Issued")

        # Phase 2: Claims
        print("\n--- Phase 2: Claims ---")
        # Need a Beneficiary user for this
        beneficiary_user_id = setup_user_with_role(ledger_id, beneficiary_node["id"], "BeneficiaryUser")
        b_headers = {"X-Actor-ID": str(beneficiary_user_id)}
        
        claim_payload = {"amount": 50000.0, "currency": "USD"}
        print("Submitting claim as Beneficiary...")
        cl_resp = requests.post(f"{BASE_URL}/ledgers/{ledger_id}/sblcs/{sblc_id}/claims", json=claim_payload, headers=b_headers)
        print(f"Status: {cl_resp.status_code}")
        if cl_resp.status_code == 200:
            print(f"✅ Claim submitted: {cl_resp.json()['id']}")

        # Phase 2: Scoping
        print("\n--- Phase 2: Scoping ---")
        # 1. Beneficiary should see this SBLC
        b_list = requests.get(f"{BASE_URL}/ledgers/{ledger_id}/sblcs", headers=b_headers).json()
        if any(s["id"] == sblc_id for s in b_list):
            print("✅ Beneficiary sees involved SBLC")
        else:
            print("❌ Beneficiary cannot see involved SBLC")

        # 2. Random applicant should NOT see this SBLC
        other_node = requests.post(f"{BASE_URL}/nodes", json={"legal_name": "Other Corp", "node_type": "applicant"}).json()
        other_user = setup_user_with_role(ledger_id, other_node["id"], "ApplicantUser")
        o_headers = {"X-Actor-ID": str(other_user)}
        o_list = requests.get(f"{BASE_URL}/ledgers/{ledger_id}/sblcs", headers=o_headers).json()
        if not any(s["id"] == sblc_id for s in o_list):
            print("✅ Other applicant correctly cannot see this SBLC")
        else:
            print("❌ Scoping failed: Other applicant sees SBLC")

    else:
        print(f"❌ Failed to create SBLC: {resp.json().get('detail')}")

def setup_user_with_role(ledger_id, node_id, role_name):
    import os, psycopg, uuid
    from dotenv import load_dotenv
    load_dotenv()
    url = os.getenv("DATABASE_URL").replace("postgresql+psycopg://", "postgresql://")
    user_id = uuid.uuid4()
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users (id, email, full_name, node_id) VALUES (%s, %s, %s, %s)",
                       (user_id, f"test-{user_id.hex[:4]}@example.com", f"Test {role_name}", node_id))
            cur.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
            r_id = cur.fetchone()[0]
            cur.execute("INSERT INTO user_ledger_roles (id, user_id, ledger_id, role_id) VALUES (%s, %s, %s, %s)",
                       (uuid.uuid4(), user_id, ledger_id, r_id))
            conn.commit()
    return user_id

if __name__ == "__main__":
    try:
        test_sblc_workflow()
    except Exception as e:
        print(f"Error during test: {e}")
