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

    def get_user_status(self, user_id: str) -> dict:
        """Get user/account status"""
        print(f"\n[DEBUG] Checking account status for user: {user_id}")
        return {
            "status": self.test_responses['account_status'],
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }

    def get_listing_status(self, listing_id: str) -> dict:
        """Get listing status"""
        print(f"\n[DEBUG] Checking listing status for: {listing_id}")
        return {
            "listing_id": listing_id,
            "status": self.test_responses['listing_status'],
            "timestamp": datetime.now().isoformat()
        }

    def can_reactivate_listing(self, block_reason: str) -> dict:
        """Check if listing can be reactivated"""
        print(f"\n[DEBUG] Checking if can reactivate listing with reason: {block_reason}")
        can_reactivate = block_reason in ["POLICY_VIOLATION", "TRADEMARK_VIOLATION"]
        return {
            "can_reactivate": can_reactivate,
            "reason_code": block_reason,
            "message": "Can be reactivated" if can_reactivate else "Cannot be reactivated",
            "timestamp": datetime.now().isoformat()
        }

    def create_support_ticket(self, user_id: str, listing_id: str, reason: str) -> dict:
        """Create a support ticket"""
        print(f"\n[DEBUG] Creating support ticket for listing: {listing_id}")
        ticket_id = f"TKT-{user_id[:4]}-{listing_id[:4]}"
        return {
            "ticket_id": ticket_id,
            "status": "CREATED",
            "user_id": user_id,
            "listing_id": listing_id,
            "reason": reason,
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