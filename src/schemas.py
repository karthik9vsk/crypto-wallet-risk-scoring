from pydantic import BaseModel
from typing import Dict

class WalletFeatures(BaseModel):
    features: Dict[str, float]