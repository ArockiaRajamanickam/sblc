import requests
import uuid
import time

BASE_URL = "http://127.0.0.1:8000"

def get_token(email, password="securePassword123!"):
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    if resp.status_code != 200:
        print(f"Login failed for {email}: {resp.text}")
        return None
    return resp.json()

def verify_workflow():
    print("🚀 Starting Phase 8 Verification (Full Lifecycle & Instrument)\n")
    
    # 1. Login as Ops
    auth = get_token("ops@gtb.com")
    if not auth: return
    token_ops = auth["access_token"]
    headers_ops = {"Authorization": f"Bearer {token_ops}"}
    
    # Get Demo Ledger
    ledgers = requests.get(f"{BASE_URL}/ledgers", headers=headers_ops).json()
    ledger_id = ledgers[0]["id"]
    # Get Nodes
    nodes = requests.get(f"{BASE_URL}/nodes", headers=headers_ops).json()
    node_issuer_id = next(n["id"] for n in nodes if "Global" in n["legal_name"])
    node_app_id = next(n["id"] for n in nodes if "Industrial" in n["legal_name"])
    node_ben_id = next(n["id"] for n in nodes if "Textile" in n["legal_name"])

    # 2. Create SBLC Draft with Instrument Fields
    print("Creating SBLC Draft...")
    sblc_payload = {
        "issuing_node_id": node_issuer_id,
        "applicant_node_id": node_app_id,
        "beneficiary_node_id": node_ben_id,
        "reference_number": f"VERIFY-P8-{uuid.uuid4().hex[:4]}",
        "amount": 250000.00,
        "currency": "USD",
        "expiry_date": "2027-12-31T23:59:59Z",
        "governing_law": "English Law",
        "applicable_rules": "UCP 600",
        "product_type": "Performance"
    }
    r_create = requests.post(f"{BASE_URL}/ledgers/{ledger_id}/sblcs", json=sblc_payload, headers=headers_ops)
    if r_create.status_code != 200:
        print(f"Failed to create SBLC: {r_create.text}")
        return
    sblc = r_create.json()
    sblc_id = sblc["id"]
    print(f"✅ Draft Created. ID: {sblc_id}, Law: {sblc['governing_law']}")

    # 3. Submit
    print("Submitting SBLC...")
    r_submit = requests.post(f"{BASE_URL}/ledgers/{ledger_id}/sblcs/{sblc_id}/submit", headers=headers_ops)
    print(f"Submit Status: {r_submit.status_code} - {r_submit.json()['status']}")
    
    # 4. Request Review (Moves to Under Review)
    print("Requesting Review...")
    r_review = requests.post(f"{BASE_URL}/ledgers/{ledger_id}/sblcs/{sblc_id}/request_review", headers=headers_ops)
    approval_id = r_review.json()["id"]
    print(f"✅ Under Review. Approval ID: {approval_id}")

    # 5. Process Approval (Moves to Approved -> Issued)
    print("Processing Approval (as Signer)...")
    auth_sig = get_token("signer@gtb.com")
    headers_sig = {"Authorization": f"Bearer {auth_sig['access_token']}"}
    
    r_approve = requests.post(f"{BASE_URL}/approvals/{approval_id}/process", 
                             json={"decision": "approved", "comments": "Final checks clear."},
                             headers=headers_sig)
    print(f"Approval Processed: {r_approve.status_code}")
    
    # 6. Final check
    time.sleep(2) # Wait for anchoring
    final_sblc = requests.get(f"{BASE_URL}/ledgers/{ledger_id}/sblcs/{sblc_id}", headers=headers_ops).json()
    print(f"Final Status: {final_sblc['status']}")
    print(f"On-Chain Status: {final_sblc['onchain_status']}")
    
    if final_sblc['status'] == 'issued' and final_sblc['onchain_status'] == 'anchored':
        print("\n✅ PHASE 8 VERIFIED: Full Workflow and Instrument Persisted!")
    else:
        print(f"\n❌ Verification Failed. Final State: {final_sblc['status']} / {final_sblc['onchain_status']}")

if __name__ == "__main__":
    verify_workflow()
