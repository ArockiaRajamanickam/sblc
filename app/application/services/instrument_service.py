from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.domain.models import FinancialInstrument, Node

class FinancialInstrumentService:
    def __init__(self, db: Session):
        self.db = db

    def issue_instrument(
        self,
        name: str,
        instrument_type: str,
        issuer_node_id: UUID,
        par_value: Decimal,
        currency: str,
        isin: Optional[str] = None,
        maturity_date: Optional[datetime] = None,
        coupon_rate: Optional[Decimal] = None,
        is_national_debt: bool = False,
        metadata_json: Optional[dict] = None
    ) -> FinancialInstrument:
        instrument = FinancialInstrument(
            name=name,
            instrument_type=instrument_type,
            issuer_node_id=issuer_node_id,
            par_value=par_value,
            currency=currency,
            isin=isin,
            maturity_date=maturity_date,
            coupon_rate=coupon_rate,
            is_national_debt=is_national_debt,
            metadata_json=metadata_json or {}
        )
        self.db.add(instrument)
        self.db.commit()
        self.db.refresh(instrument)
        return instrument

    def get_instruments(self, issuer_id: Optional[UUID] = None) -> List[FinancialInstrument]:
        query = select(FinancialInstrument)
        if issuer_id:
            query = query.where(FinancialInstrument.issuer_node_id == issuer_id)
        return self.db.scalars(query).all()

    def get_instrument_by_isin(self, isin: str) -> Optional[FinancialInstrument]:
        return self.db.execute(
            select(FinancialInstrument).where(FinancialInstrument.isin == isin)
        ).scalar()
