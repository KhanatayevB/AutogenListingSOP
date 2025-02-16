import json
from typing import Dict, Any
from datetime import datetime

class FlipkartAPIHandler:
    def __init__(self, test_responses: Dict[str, str] = None):
        """Initialize with test responses"""
        self.test_responses = test_responses or {
            'account_status': 'ACTIVE',
            'listing_status': 'ACTIVE',
            'block_reason': 'SELLER_STATE_CHANGE',
            'brand_approval': 'PENDING'
        }

    def check_account_status(self, seller_id: str) -> dict:
        """Simulate account status API call"""
        print(f"\n[DEBUG] Checking account status for seller: {seller_id}")
        return {
            "status": self.test_responses['account_status'],
            "seller_id": seller_id,
            "timestamp": datetime.now().isoformat()
        }

    def check_listing_status(self, listing_id: str) -> dict:
        """Simulate listing status API call"""
        print(f"\n[DEBUG] Checking listing status for: {listing_id}")
        return {
            "listing_id": listing_id,
            "status": self.test_responses['listing_status'],
            "timestamp": datetime.now().isoformat()
        }

    def get_block_reason(self, listing_id: str) -> dict:
        """Simulate block reason API call"""
        print(f"\n[DEBUG] Getting block reason for: {listing_id}")
        return {
            "listing_id": listing_id,
            "reason": self.test_responses['block_reason'],
            "details": "Simulated block reason response",
            "timestamp": datetime.now().isoformat()
        }

    def check_brand_approval(self, brand_id: str) -> dict:
        """Simulate brand approval API call"""
        print(f"\n[DEBUG] Checking brand approval for: {brand_id}")
        return {
            "brand_id": brand_id,
            "status": self.test_responses['brand_approval'],
            "timestamp": datetime.now().isoformat()
        }

    def get_override_status(self, listing_id: str) -> dict:
        """Simulate override status API call"""
        print(f"\n[DEBUG] Getting override status for: {listing_id}")
        block_reason = self.test_responses['block_reason']
        return {
            "listing_id": listing_id,
            "overrides": [block_reason] if block_reason in ["TRADEMARK_VIOLATION", "POLICY_VIOLATION"] else [],
            "count": 1 if block_reason in ["TRADEMARK_VIOLATION", "POLICY_VIOLATION"] else 0,
            "timestamp": datetime.now().isoformat()
        } 