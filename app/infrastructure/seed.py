from __future__ import annotations

import uuid
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.db import SessionLocal
from app.domain.models import Permission, Role, RolePermission


PERMISSIONS: Dict[str, str] = {
    # Ledger / Admin
    "ledger.create": "Create a new ledger",
    "ledger.manage": "Manage ledger settings (rename, deactivate)",

    # Node / Membership
    "node.create": "Create node records",
    "node.manage": "Manage node records (edit, deactivate)",
    "node.invite": "Invite a node to join a ledger",
    "membership.assign": "Assign roles to a node within a ledger",
    "membership.suspend": "Suspend/remove memberships",

    # SBLC Workflow
    "sblc.create": "Create SBLC drafts",
    "sblc.review": "Review SBLC drafts / request changes",
    "sblc.approve": "Approve SBLC for issuance",
    "sblc.issue": "Issue/sign SBLC",
    "sblc.amend": "Create/approve SBLC amendments",
    "sblc.cancel": "Cancel/close SBLC (if supported)",

    # Claims
    "claim.submit": "Submit claim package",
    "claim.review": "Review claim package",
    "claim.decide": "Accept/reject claim",
    "claim.pay": "Record payment action",

    # Audit
    "audit.read": "Read audit events",
}


ROLES: Dict[str, str] = {
    "IssuerAdmin": "Issuer administrator (full access)",
    "IssuerSigner": "Issuer signer for issuance/amendments and claim decisions",
    "IssuerOps": "Issuer operations (create/review/approve SBLC)",
    "ApplicantUser": "Applicant user (create drafts, view audit)",
    "BeneficiaryUser": "Beneficiary user (submit claims, view audit)",
    "AdvisorBank": "Advising/confirming bank (review + read audit)",
    "AuditorReadOnly": "Auditor/regulator read-only access",
    "SwiftReviewer": "Reviewer for SWIFT message compliance",
    "CIB_Ops": "Corporate & Institutional Banking Operations",
    "ComplianceOfficer": "Enhanced AML/KYC reviewer",
}


ROLE_PERMISSION_MAP: Dict[str, List[str]] = {
    "IssuerAdmin": list(PERMISSIONS.keys()),
    "IssuerSigner": [
        "sblc.issue",
        "sblc.amend",
        "claim.decide",
        "audit.read",
    ],
    "IssuerOps": [
        "sblc.create",
        "sblc.review",
        "sblc.approve",
        "audit.read",
    ],
    "ApplicantUser": [
        "sblc.create",
        "sblc.review",
        "audit.read",
    ],
    "BeneficiaryUser": [
        "claim.submit",
        "audit.read",
    ],
    "AdvisorBank": [
        "sblc.review",
        "audit.read",
    ],
    "AuditorReadOnly": [
        "audit.read",
    ],
    "SwiftReviewer": [
        "sblc.review",
        "audit.read",
    ],
    "CIB_Ops": [
        "sblc.create",
        "sblc.review",
        "sblc.approve",
        "audit.read",
    ],
    "ComplianceOfficer": [
        "sblc.review",
        "claim.review",
        "audit.read",
    ],
}


def upsert_permissions(session: Session) -> Dict[str, Permission]:
    out: Dict[str, Permission] = {}
    for code, desc in PERMISSIONS.items():
        existing = session.scalar(select(Permission).where(Permission.code == code))
        if existing:
            if existing.description != desc:
                existing.description = desc
            out[code] = existing
        else:
            p = Permission(id=uuid.uuid4(), code=code, description=desc)
            session.add(p)
            out[code] = p
    session.flush()
    return out


def upsert_roles(session: Session) -> Dict[str, Role]:
    out: Dict[str, Role] = {}
    for name, desc in ROLES.items():
        existing = session.scalar(select(Role).where(Role.name == name))
        if existing:
            if existing.description != desc:
                existing.description = desc
            out[name] = existing
        else:
            r = Role(id=uuid.uuid4(), name=name, description=desc)
            session.add(r)
            out[name] = r
    session.flush()
    return out


def ensure_role_permissions(session: Session, roles: Dict[str, Role], perms: Dict[str, Permission]) -> None:
    existing_links = set(
        session.execute(select(RolePermission.role_id, RolePermission.permission_id)).all()
    )

    for role_name, perm_codes in ROLE_PERMISSION_MAP.items():
        role = roles[role_name]
        for code in perm_codes:
            perm = perms[code]
            key = (role.id, perm.id)
            if key not in existing_links:
                session.add(RolePermission(role_id=role.id, permission_id=perm.id))


def setup_demo_data(session: Session, roles: Dict[str, Role]) -> None:
    from app.domain.models import Node, User, Ledger, LedgerMembership, UserLedgerRole
    from app.infrastructure.security.auth import get_password_hash
    
    # 1. Create Nodes
    node_data_list = [
        {"legal_name": "Global Trade Bank", "display_name": "GTB Issuer", "node_type": "issuer_bank", "key": "GTB"},
        {"legal_name": "Standard Advise Corp", "display_name": "Standard Advising", "node_type": "advising_bank", "key": "Standard"},
        {"legal_name": "Industrial Imports Ltd", "display_name": "Industrial Imports", "node_type": "applicant", "key": "Industrial"},
        {"legal_name": "Textile Exports Inc", "display_name": "Textile Exports", "node_type": "beneficiary", "key": "Textile"}
    ]
    
    node_obj_map = {}
    for nd in node_data_list:
        existing = session.scalar(select(Node).where(Node.legal_name == nd["legal_name"]))
        if not existing:
            n = Node(id=uuid.uuid4(), legal_name=nd["legal_name"], display_name=nd["display_name"], node_type=nd["node_type"])
            session.add(n)
            node_obj_map[nd["key"]] = n
        else:
            node_obj_map[nd["key"]] = existing
    session.flush()

    node_issuer = node_obj_map["GTB"]
    node_applicant = node_obj_map["Industrial"]
    node_beneficiary = node_obj_map["Textile"]

    # 2. Create Users
    pwd = get_password_hash("securePassword123!")
    users_data = [
        {"email": "ops@gtb.com", "full_name": "GTB Ops User", "node_id": node_issuer.id},
        {"email": "signer@gtb.com", "full_name": "GTB Signer User", "node_id": node_issuer.id},
        {"email": "user@industrial.com", "full_name": "Industrial App User", "node_id": node_applicant.id},
        {"email": "ops@textile.com", "full_name": "Textile Ben User", "node_id": node_beneficiary.id}
    ]
    
    user_obj_map = {}
    for u_data in users_data:
        existing = session.scalar(select(User).where(User.email == u_data["email"]))
        if not existing:
            u = User(id=uuid.uuid4(), email=u_data["email"], full_name=u_data["full_name"], hashed_password=pwd, node_id=u_data["node_id"])
            session.add(u)
            user_obj_map[u_data["email"]] = u
        else:
            user_obj_map[u_data["email"]] = existing
    session.flush()

    user_iss_ops = user_obj_map["ops@gtb.com"]
    user_iss_signer = user_obj_map["signer@gtb.com"]
    user_app = user_obj_map["user@industrial.com"]
    user_ben = user_obj_map["ops@textile.com"]

    # 3. Create Demo Ledger
    ledger_name = "Global Trade Corridor"
    ledger = session.scalar(select(Ledger).where(Ledger.name == ledger_name))
    if not ledger:
        ledger = Ledger(id=uuid.uuid4(), name=ledger_name, description="Primary trade route SBLCs")
        session.add(ledger)
        session.flush()

    # 4. Memberships
    memberships = [
        (node_issuer.id, roles["IssuerAdmin"].id),
        (node_obj_map["Standard"].id, roles["AdvisorBank"].id),
        (node_applicant.id, roles["ApplicantUser"].id),
        (node_beneficiary.id, roles["BeneficiaryUser"].id)
    ]
    
    for n_id, r_id in memberships:
        existing = session.scalar(select(LedgerMembership).where(
            LedgerMembership.ledger_id == ledger.id,
            LedgerMembership.node_id == n_id,
            LedgerMembership.role_id == r_id
        ))
        if not existing:
            session.add(LedgerMembership(id=uuid.uuid4(), ledger_id=ledger.id, node_id=n_id, role_id=r_id, status="active"))
    session.flush()

    # 5. User Roles within Ledger
    user_roles_data = [
        (user_iss_ops.id, roles["IssuerOps"].id),
        (user_iss_signer.id, roles["IssuerSigner"].id),
        (user_app.id, roles["ApplicantUser"].id),
        (user_ben.id, roles["BeneficiaryUser"].id)
    ]

    for u_id, r_id in user_roles_data:
        existing = session.scalar(select(UserLedgerRole).where(
            UserLedgerRole.user_id == u_id,
            UserLedgerRole.ledger_id == ledger.id,
            UserLedgerRole.role_id == r_id
        ))
        if not existing:
            session.add(UserLedgerRole(id=uuid.uuid4(), user_id=u_id, ledger_id=ledger.id, role_id=r_id))

    print(f"✅ Demo Data Ready: Ledger '{ledger.name}'")


def main() -> None:
    session = SessionLocal()
    try:
        with session.begin():
            perms = upsert_permissions(session)
            roles = upsert_roles(session)
            ensure_role_permissions(session, roles, perms)
            setup_demo_data(session, roles)
        print("✅ Seed and demo complete")
    finally:
        session.close()


if __name__ == "__main__":
    main()
