import time
import random
from collections import defaultdict

class AuctionSystem:
    def __init__(self):
        self.bidder_stats = defaultdict(lambda: {'wins': 0, 'bids': 0})
        self.min_acceptable_price_history = []
        self.last_processed_time = time.time()
        
    def calculate_bid_score(self, bid, user_match_bonus):
        base_score = bid['bid_price'] * bid['quality_score']
        if bid['user_match']:
            base_score *= (1 + user_match_bonus)
        return base_score
        
    def update_bidder_stats(self, bidder_id, won):
        self.bidder_stats[bidder_id]['bids'] += 1
        if won:
            self.bidder_stats[bidder_id]['wins'] += 1
            
    def get_bidder_win_rate(self, bidder_id):
        stats = self.bidder_stats[bidder_id]
        if stats['bids'] == 0:
            return 0
        return stats['wins'] / stats['bids']
        
    def adjust_min_acceptable_price(self, current_map):
        now = time.time()
        time_elapsed = now - self.last_processed_time
        self.last_processed_time = now
        
        if len(self.min_acceptable_price_history) > 10:
            avg_map = sum(self.min_acceptable_price_history[-10:]) / 10
            if current_map < avg_map * 0.9:
                return avg_map * 0.9
        return current_map
        
    def process_auction(self, request, bids, user_match_bonus, min_acceptable_price):
        valid_bids = [bid for bid in bids if bid['bid_price'] >= min_acceptable_price]
        
        if not valid_bids:
            return {
                "request_id": request["request_id"],
                "bidder_id": "None"
            }
            
        min_acceptable_price = self.adjust_min_acceptable_price(min_acceptable_price)
        self.min_acceptable_price_history.append(min_acceptable_price)
        
        for bid in valid_bids:
            bid['score'] = self.calculate_bid_score(bid, user_match_bonus)
            win_rate = self.get_bidder_win_rate(bid['bidder_id'])
            bid['score'] *= max(0.5, 1 - win_rate)  # Fairness adjustment
            
        valid_bids.sort(key=lambda x: (-x['score'], x['bid_price']))
        
        winner = valid_bids[0]
        self.update_bidder_stats(winner['bidder_id'], True)
        
        for bid in valid_bids[1:]:
            self.update_bidder_stats(bid['bidder_id'], False)
            
        return {
            "request_id": request["request_id"],
            "bidder_id": winner["bidder_id"]
        }