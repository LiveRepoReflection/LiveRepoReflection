import unittest
import time
from bandwidth_allocation import allocate_bandwidth

class TestBandwidthAllocation(unittest.TestCase):
    def setUp(self):
        # Fixed block timestamp for testing
        self.current_timestamp = 1000000
        # Define a valid time window range (e.g., ±300 seconds)
        self.valid_window = 300
        # Dummy public key mapping for users
        self.public_keys = {
            "userA": "pubkeyA",
            "userB": "pubkeyB",
            "userC": "pubkeyC"
        }
        # Initial credit balances for users
        self.initial_credits = {
            "userA": 100,
            "userB": 100,
            "userC": 100
        }
        # For simplicity, assume our dummy signature check in implementation expects "valid"
        self.valid_signature = "valid"
    
    def valid_timestamp(self, offset=0):
        return self.current_timestamp + offset

    def create_transaction(self, user_id, bandwidth_request, credits_offered, nonce, timestamp_offset=0, signature=None):
        if signature is None:
            signature = self.valid_signature
        return {
            "user_id": user_id,
            "bandwidth_request": bandwidth_request,
            "credits_offered": credits_offered,
            "nonce": nonce,
            "timestamp": self.valid_timestamp(timestamp_offset),
            "signature": signature
        }

    def test_valid_allocation_proportional(self):
        # Two valid transactions. Test max cap enforcement.
        # Available bandwidth is 100 Mbps.
        # Max cap is 50% (i.e., 50 Mbps maximum per user).
        transactions = [
            self.create_transaction("userA", 80, 40, nonce=1),
            self.create_transaction("userB", 60, 60, nonce=1)
        ]
        total_bandwidth = 100
        max_cap = 0.5  # 50% cap
        
        # Expected behavior:
        # Total offered credits = 40 + 60 = 100.
        # Ideal entitlement:
        #   userA: 40/100 * 100 = 40 Mbps; allocated = min(request 80, 40, cap 50) = 40 Mbps.
        #   userB: 60/100 * 100 = 60 Mbps capped to 50 (max cap) = 50 Mbps.
        # No further proportional reduction as allocated total 90 <= 100.
        # Credit deduction calculated proportionally:
        #   userA: deducted = 40 * (40/80) = 20; new balance = 100 - 20 = 80.
        #   userB: deducted = 60 * (50/60) = 50; new balance = 100 - 50 = 50.
        expected_allocation = {
            "userA": 40,
            "userB": 50
        }
        expected_credits = {
            "userA": 80,
            "userB": 50,
            "userC": 100  # no transaction
        }
        
        allocation, updated_credits = allocate_bandwidth(
            transactions,
            total_bandwidth,
            self.initial_credits.copy(),
            self.public_keys,
            max_cap,
            self.current_timestamp
        )
        self.assertEqual(allocation, expected_allocation)
        self.assertEqual(updated_credits, expected_credits)

    def test_invalid_signature(self):
        # Transaction with invalid signature should raise ValueError
        transactions = [
            self.create_transaction("userA", 50, 30, nonce=1, signature="invalid")
        ]
        total_bandwidth = 100
        max_cap = 1.0  # 100% cap for this test

        with self.assertRaises(ValueError) as context:
            allocate_bandwidth(
                transactions,
                total_bandwidth,
                self.initial_credits.copy(),
                self.public_keys,
                max_cap,
                self.current_timestamp
            )
        self.assertIn("Invalid signature", str(context.exception))

    def test_insufficient_credits(self):
        # Transaction where user does not have enough credits should raise ValueError.
        # Set userA's credits less than credits_offered.
        initial_credits = self.initial_credits.copy()
        initial_credits["userA"] = 10  # insufficient for offered 30 credits
        
        transactions = [
            self.create_transaction("userA", 50, 30, nonce=1)
        ]
        total_bandwidth = 100
        max_cap = 1.0

        with self.assertRaises(ValueError) as context:
            allocate_bandwidth(
                transactions,
                total_bandwidth,
                initial_credits,
                self.public_keys,
                max_cap,
                self.current_timestamp
            )
        self.assertIn("Insufficient credits", str(context.exception))

    def test_invalid_nonce(self):
        # Transaction with nonce not greater than previous nonce should raise ValueError.
        transactions = [
            self.create_transaction("userA", 50, 30, nonce=2),
            self.create_transaction("userA", 40, 20, nonce=2)  # duplicate nonce
        ]
        total_bandwidth = 100
        max_cap = 1.0

        with self.assertRaises(ValueError) as context:
            allocate_bandwidth(
                transactions,
                total_bandwidth,
                self.initial_credits.copy(),
                self.public_keys,
                max_cap,
                self.current_timestamp
            )
        self.assertIn("Invalid nonce", str(context.exception))

    def test_invalid_timestamp(self):
        # Transaction with a timestamp too old should raise ValueError.
        transactions = [
            # timestamp is 10 minutes older than current acceptable window (older than 300 seconds)
            self.create_transaction("userA", 50, 30, nonce=1, timestamp_offset=-400)
        ]
        total_bandwidth = 100
        max_cap = 1.0

        with self.assertRaises(ValueError) as context:
            allocate_bandwidth(
                transactions,
                total_bandwidth,
                self.initial_credits.copy(),
                self.public_keys,
                max_cap,
                self.current_timestamp
            )
        self.assertIn("Invalid timestamp", str(context.exception))

    def test_proportional_allocation_with_unused_entitlement(self):
        # Test scenario where one user's request is fully satisfied (less than entitlement)
        # thereby reallocating remaining bandwidth to other users.
        # userA requests 10 (and offers high credits so that ideal share would have been high)
        # userB requests 100.
        # Total offered credits = 50 (A) + 100 (B) = 150.
        # Ideal entitlement:
        #   userA: (50/150)*100 = 33.33, but request is 10 so gets full 10.
        #   userB: initially entitled (100/150)*100 = 66.67, but then gets the remaining bandwidth (100 - 10 = 90)
        # Credit deduction:
        #   userA: deducted = 50 * (10/10) = 50.
        #   userB: deducted = 100 * (90/100) = 90.
        transactions = [
            self.create_transaction("userA", 10, 50, nonce=1),
            self.create_transaction("userB", 100, 100, nonce=1)
        ]
        total_bandwidth = 100
        max_cap = 1.0  # no cap
        
        expected_allocation = {
            "userA": 10,
            "userB": 90
        }
        expected_credits = {
            "userA": self.initial_credits["userA"] - 50,
            "userB": self.initial_credits["userB"] - 90,
            "userC": self.initial_credits["userC"]
        }
        
        allocation, updated_credits = allocate_bandwidth(
            transactions,
            total_bandwidth,
            self.initial_credits.copy(),
            self.public_keys,
            max_cap,
            self.current_timestamp
        )
        self.assertEqual(allocation, expected_allocation)
        self.assertEqual(updated_credits, expected_credits)

    def test_max_cap_enforcement(self):
        # Test where a user's computed entitlement exceeds the maximum cap.
        # userB should be capped at maximum allowed bandwidth.
        transactions = [
            self.create_transaction("userA", 50, 30, nonce=1),
            self.create_transaction("userB", 100, 100, nonce=1)
        ]
        total_bandwidth = 200
        max_cap = 0.3  # maximum 30% of total bandwidth = 60 Mbps for any user
        
        # Total offered credits = 30 + 100 = 130.
        # Ideal entitlement:
        #   userA: 30/130 * 200 ≈ 46.15 Mbps, so allocated = min(50, 46.15, 60) = 46.15 Mbps.
        #   userB: 100/130 * 200 ≈ 153.85 Mbps, but capped to 60.
        # Total allocated = 46.15 + 60 = 106.15 Mbps which is less than available so no further scaling.
        # Credit deduction:
        #   userA: 30 * (46.15/50) ≈ 27.69 (rounded to two decimals).
        #   userB: 100 * (60/100) = 60.
        expected_allocation = {
            "userA": 46.15,
            "userB": 60
        }
        expected_credits = {
            "userA": round(self.initial_credits["userA"] - (30 * (46.15/50)), 2),
            "userB": self.initial_credits["userB"] - 60,
            "userC": self.initial_credits["userC"]
        }
        allocation, updated_credits = allocate_bandwidth(
            transactions,
            total_bandwidth,
            self.initial_credits.copy(),
            self.public_keys,
            max_cap,
            self.current_timestamp
        )
        # Allow a small delta for floating point comparisons.
        self.assertAlmostEqual(allocation["userA"], expected_allocation["userA"], places=2)
        self.assertAlmostEqual(allocation["userB"], expected_allocation["userB"], places=2)
        self.assertAlmostEqual(updated_credits["userA"], expected_credits["userA"], places=2)
        self.assertAlmostEqual(updated_credits["userB"], expected_credits["userB"], places=2)
        self.assertEqual(updated_credits["userC"], expected_credits["userC"])

if __name__ == "__main__":
    unittest.main()