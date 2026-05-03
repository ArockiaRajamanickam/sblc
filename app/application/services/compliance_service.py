from __future__ import annotations
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException
from app.domain.models import Node, Ledger, User, WireTransaction, CentralBankGateway
from sqlalchemy.orm import Session
from sqlalchemy import select
from decimal import Decimal

class SovereigntyViolation(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=403, detail=f"Sovereignty Violation: {detail}")

class ComplianceService:
    def __init__(self, db: Session):
        self.db = db
        # Sanction list mock (country codes)
        self.sanctioned_countries = ["KP", "IR", "SY", "CU"]
        # Central Bank Portals mock mapping
        self.cb_portal_map = {
            "UK": "https://portal.bankofengland.co.uk",
            "CN": "https://portal.bankofchina.com",
            "US": "https://portal.fedreserve.gov"
        }

    def validate_sovereignty(
        self, 
        actor_id: UUID, 
        entity_id: UUID, 
        entity_type: str = "ledger"
    ):
        """
        Ensures that the actor's region matches the entity's region.
        In a real institutional setting, this might check specific jurisdictional policies.
        """
        actor = self.db.get(User, actor_id)
        if not actor:
            raise SovereigntyViolation("Actor not found")

        if entity_type == "ledger":
            entity = self.db.get(Ledger, entity_id)
        elif entity_type == "node":
            entity = self.db.get(Node, entity_id)
        elif entity_type == "sblc":
            from app.domain.models import SBLC
            sblc = self.db.get(SBLC, entity_id)
            entity = sblc.ledger if sblc else None
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")

        if not entity:
            raise SovereigntyViolation(f"{entity_type.capitalize()} not found")

        # Global admins might bypass this, but for Phase 3 we enforce strict fencing
        if actor.region_id != entity.region_id:
            raise SovereigntyViolation(
                f"Access Denied. Actor is in {actor.region_id}, while data is restricted to {entity.region_id}"
            )

    def get_effective_region(self, entity_id: UUID, entity_type: str = "ledger") -> str:
        if entity_type == "ledger":
            entity = self.db.get(Ledger, entity_id)
        elif entity_type == "node":
            entity = self.db.get(Node, entity_id)
        elif entity_type == "sblc":
            from app.domain.models import SBLC
            sblc = self.db.get(SBLC, entity_id)
            entity = sblc.ledger if sblc else None
        
        return entity.region_id if entity else "Unknown"

    def generate_sblc_report(self, region_id: Optional[str] = None):
        """
        Generates a summary report of all SBLCs, optionally filtered by region.
        """
        from app.domain.models import SBLC
        from sqlalchemy import select
        
        query = select(SBLC)
        if region_id:
            # We join with Ledger to filter by region
            query = query.join(Ledger).where(Ledger.region_id == region_id)
        
        sblcs = self.db.scalars(query).all()
        
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "region": region_id or "GLOBAL",
            "total_count": len(sblcs),
            "data": [
                {
                    "id": str(s.id),
                    "reference": s.reference_number,
                    "amount": f"{s.amount} {s.currency}",
                    "status": str(s.status),
                    "onchain_status": str(s.onchain_status),
                    "issuing_node": s.issuing_node.legal_name,
                    "applicant_node": s.applicant_node.legal_name,
                    "beneficiary_node": s.beneficiary_node.legal_name,
                    "created_at": s.created_at.isoformat()
                }
                for s in sblcs
            ]
        }
        return report

    def check_transaction(self, tx_id: UUID) -> bool:
        tx = self.db.get(WireTransaction, tx_id)
        if not tx: return False

        sender = tx.sender
        receiver = tx.receiver
        
        # 1. Check sanction list (Country-based)
        if (sender.node.country_code in self.sanctioned_countries) or \
           (receiver.node.country_code in self.sanctioned_countries):
            tx.status = "held_compliance"
            tx.is_sanction_check_passed = False
            tx.is_flagged = True
            tx.flag_reason = "Sanctioned country detected"
            self.db.commit()
            return False

        # 2. Check risk score behavior (Mock)
        if sender.compliance_score < 50:
             tx.status = "held_compliance"
             tx.is_flagged = True
             tx.flag_reason = "Sender compliance score too low"
             self.db.commit()
             return False

        tx.is_sanction_check_passed = True
        return True

    def query_cb_portal(self, country_code: str, account_number: str) -> Dict[str, str]:
        portal_url = self.cb_portal_map.get(country_code, "https://global.centralbank.org")
        # In real system, this makes an API call. Here we return mock status.
        return {
            "portal": portal_url,
            "account_status": "authorized",
            "allowance_limit_usd": str(Decimal("50000000.00")),
            "last_verified_cb": datetime.now(timezone.utc).isoformat()
        }

    def register_cb_gateway(self, name: str, region_code: str, portal_url: str):
        gateway = CentralBankGateway(
            name=name,
            region_code=region_code,
            portal_url=portal_url,
            allowance_limit=Decimal("1000000000.00") # $1B default limit
        )
        self.db.add(gateway)
        self.db.commit()
