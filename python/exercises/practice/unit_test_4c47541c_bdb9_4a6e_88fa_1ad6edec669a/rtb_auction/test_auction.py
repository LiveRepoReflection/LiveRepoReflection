import unittest
import random
import time
from rtb_auction.auction import AuctionSystem

class TestRTBAuction(unittest.TestCase):
    def setUp(self):
        self.auction = AuctionSystem()
        self.bidders = ["bidder1", "bidder2", "bidder3", "bidder4"]
        self.user_match_bonus = 0.2
        self.min_acceptable_price = 50  # in cents
        
    def test_single_auction(self):
        request = {
            "request_id": "req1",
            "user_id": "user1",
            "ad_slot_id": "slot1",
            "user_context": {"location": "US", "browser": "chrome"},
            "timestamp": int(time.time() * 1000)
        }
        
        bids = [
            {
                "request_id": "req1",
                "bidder_id": "bidder1",
                "bid_price": 100,
                "user_match": True,
                "ad_creative": "ad1",
                "quality_score": 0.9
            },
            {
                "request_id": "req1",
                "bidder_id": "bidder2",
                "bid_price": 120,
                "user_match": False,
                "ad_creative": "ad2",
                "quality_score": 0.8
            }
        ]
        
        winner = self.auction.process_auction(request, bids, self.user_match_bonus, self.min_acceptable_price)
        self.assertEqual(winner["request_id"], "req1")
        self.assertEqual(winner["bidder_id"], "bidder1")  # Should win due to user match bonus
        
    def test_no_valid_bids(self):
        request = {
            "request_id": "req2",
            "user_id": "user2",
            "ad_slot_id": "slot1",
            "user_context": {"location": "UK", "browser": "firefox"},
            "timestamp": int(time.time() * 1000)
        }
        
        bids = [
            {
                "request_id": "req2",
                "bidder_id": "bidder3",
                "bid_price": 30,  # Below MAP
                "user_match": True,
                "ad_creative": "ad3",
                "quality_score": 0.95
            }
        ]
        
        winner = self.auction.process_auction(request, bids, self.user_match_bonus, self.min_acceptable_price)
        self.assertEqual(winner["request_id"], "req2")
        self.assertEqual(winner["bidder_id"], "None")
        
    def test_performance(self):
        num_auctions = 1000
        start_time = time.time()
        
        for i in range(num_auctions):
            request = {
                "request_id": f"req_{i}",
                "user_id": f"user_{i%100}",
                "ad_slot_id": "slot1",
                "user_context": {"location": random.choice(["US", "UK", "CA"]), "browser": random.choice(["chrome", "firefox", "safari"])},
                "timestamp": int(time.time() * 1000)
            }
            
            bids = []
            for bidder in random.sample(self.bidders, random.randint(1, 4)):
                bids.append({
                    "request_id": f"req_{i}",
                    "bidder_id": bidder,
                    "bid_price": random.randint(50, 500),
                    "user_match": random.random() > 0.7,
                    "ad_creative": f"ad_{bidder}",
                    "quality_score": round(random.uniform(0.5, 1.0), 2)
                })
                
            self.auction.process_auction(request, bids, self.user_match_bonus, self.min_acceptable_price)
            
        elapsed = time.time() - start_time
        avg_latency = (elapsed / num_auctions) * 1000  # in milliseconds
        self.assertLess(avg_latency, 10, f"Average latency of {avg_latency:.2f}ms exceeds 10ms target")
        
    def test_fairness(self):
        win_counts = {bidder: 0 for bidder in self.bidders}
        total_auctions = 1000
        
        for i in range(total_auctions):
            request = {
                "request_id": f"req_fair_{i}",
                "user_id": f"user_{i%100}",
                "ad_slot_id": "slot1",
                "user_context": {"location": "US", "browser": "chrome"},
                "timestamp": int(time.time() * 1000)
            }
            
            bids = []
            for bidder in self.bidders:
                bids.append({
                    "request_id": f"req_fair_{i}",
                    "bidder_id": bidder,
                    "bid_price": random.randint(100, 200),
                    "user_match": random.random() > 0.7,
                    "ad_creative": f"ad_{bidder}",
                    "quality_score": 0.9
                })
                
            winner = self.auction.process_auction(request, bids, self.user_match_bonus, self.min_acceptable_price)
            if winner["bidder_id"] != "None":
                win_counts[winner["bidder_id"]] += 1
                
        min_win_pct = min(win_counts.values()) / total_auctions
        max_win_pct = max(win_counts.values()) / total_auctions
        self.assertGreater(min_win_pct, 0.15, "Fairness not maintained - some bidders winning <15% of auctions")
        self.assertLess(max_win_pct, 0.35, "Fairness not maintained - some bidders winning >35% of auctions")

if __name__ == '__main__':
    unittest.main()