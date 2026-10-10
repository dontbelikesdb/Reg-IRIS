from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class TradeReport(BaseModel):
    Trade_ID: str = Field(..., max_length=12, pattern="^[a-zA-Z0-9]+$")
    Asset_Class: Literal["Equity", "Bond", "FX", "Derivative", "Commodity"]
    Timestamp: datetime
    Counterparty_LEI: str = Field(..., pattern="^[0-9A-Z]{20}$")
    Price: float = Field(..., ge=0)
    Quantity: int = Field(..., ge=1)
    Currency: Literal["USD", "EUR", "GBP", "JPY", "CHF"]
    Maturity_Date: Optional[date] = None
    Underlying_ISIN: Optional[str] = Field(None, pattern="^[A-Z0-9]{12}$")