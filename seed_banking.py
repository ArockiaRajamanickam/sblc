from app.infrastructure.db import SessionLocal
from app.application.services.banking_service import BankingService
from app.domain.models import Node, InstitutionAccount, WireTransaction, FinancialInstrument, DigitalWallet
from sqlalchemy import select, func
from decimal import Decimal
from datetime import datetime, timezone

def seed_banking_records():
    db = SessionLocal()
    service = BankingService(db)
    
    try:
        # 1. Get some nodes to act as owners
        nodes = db.scalars(select(Node).limit(3)).all()
        if not nodes:
            print("No nodes found. Run initial seed first.")
            return

        # 2. Seed external banks metadata
        service.seed_external_banks()
        print("Seeded external banks.")

        # 3. Create Master Accounts
        def get_or_create_account(acc_num, **kwargs):
            existing = db.execute(select(InstitutionAccount).where(InstitutionAccount.account_number == acc_num)).scalar()
            if existing: return existing
            return service.create_account(account_number=acc_num, **kwargs)

        master1 = get_or_create_account(
            "SG-DBS-1100223344",
            node_id=nodes[0].id,
            currency="USD",
            account_type="master"
        )
        master1.balance = Decimal("25000000.00")
        
        master2 = get_or_create_account(
            "GB-BARC-9988776655",
            node_id=nodes[1].id,
            currency="GBP",
            account_type="master",
            is_nostro=True
        )
        master2.balance = Decimal("15000000.00")
        
        db.commit()
        print(f"Master Accounts verified/created: {master1.account_number}, {master2.account_number}")

        # 4. Create Sub Accounts
        sub1 = get_or_create_account(
            "SG-DBS-SUB-001",
            node_id=nodes[0].id,
            currency="USD",
            account_type="sub_account",
            parent_id=master1.id
        )
        sub1.balance = Decimal("5000000.00")
        
        db.commit()
        print(f"Sub Account verified/created: {sub1.account_number}")

        # 5. Initiate a Transfer (Only if not many exist)
        tx_count = db.execute(select(func.count(WireTransaction.id))).scalar()
        if tx_count < 5:
            tx = service.initiate_wire_transfer(
                sender_id=master1.id,
                receiver_id=master2.id,
                amount=Decimal("1200000.00"),
                currency="USD",
                reference="SWIFT-PAY-MARCH-INST-01"
            )
            print(f"Initiated Wire Transfer: {tx.reference} (Status: {tx.status})")

        # 6. Seed Financial Instruments
        from app.application.services.instrument_service import FinancialInstrumentService
        inst_service = FinancialInstrumentService(db)
        
        existing_bond = db.execute(select(FinancialInstrument).where(FinancialInstrument.isin == "GB00B16NNR78")).scalar()
        if not existing_bond:
            bond = inst_service.issue_instrument(
                name="UK Treasury Gilt 2026",
                instrument_type="national_debt",
                issuer_node_id=nodes[0].id,
                par_value=Decimal("100000000.00"),
                currency="GBP",
                isin="GB00B16NNR78",
                maturity_date=datetime(2026, 12, 31, tzinfo=timezone.utc),
                coupon_rate=Decimal("0.0425"),
                is_national_debt=True
            )
            print(f"Issued Financial Instrument: {bond.name} ({bond.isin})")

        # 7. Seed Digital Wallets
        from app.application.services.digital_wallet_service import DigitalWalletService
        wallet_service = DigitalWalletService(db)
        
        existing_wallet = db.execute(select(DigitalWallet).where(DigitalWallet.address == "bc1q9institutionalvaultaddr001")).scalar()
        if not existing_wallet:
            wallet = wallet_service.register_wallet(
                node_id=nodes[0].id,
                wallet_type="institutional_vault",
                address="bc1q9institutionalvaultaddr001",
                metadata_json={"provider": "Fireblocks", "custodian": "DBS"}
            )
            wallet_service.verify_wallet(wallet.id, nodes[0].id)
            print(f"Registered & Verified Wallet: {wallet.address}")

    finally:
        db.close()

if __name__ == "__main__":
    seed_banking_records()
