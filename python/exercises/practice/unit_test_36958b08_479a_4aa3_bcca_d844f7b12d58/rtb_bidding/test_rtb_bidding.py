import unittest
from rtb_bidding.rtb_bidding import process_bid_request

class TestRTBBidding(unittest.TestCase):
    def setUp(self):
        # Sample targeting criteria database
        self.targeting_criteria = [
            {
                'criterion_id': 'crit1',
                'target_user_ids': {'user1', 'user2'},
                'target_devices': {'mobile', 'tablet'},
                'target_locations': [
                    {'country': 'US', 'region': 'California', 'city': 'Los Angeles'},
                    {'country': 'CA', 'region': 'Ontario', 'city': 'Toronto'}
                ],
                'target_ad_categories': {'sports', 'news'},
                'bid_price': 2.5
            },
            {
                'criterion_id': 'crit2',
                'target_user_ids': set(),
                'target_devices': {'desktop'},
                'target_locations': [
                    {'country': '*', 'region': '*', 'city': '*'}
                ],
                'target_ad_categories': {'technology'},
                'bid_price': 1.8
            }
        ]

    def test_exact_match(self):
        bid_request = {
            'request_id': 'req1',
            'user_id': 'user1',
            'device': 'mobile',
            'location': {
                'country': 'US',
                'region': 'California',
                'city': 'Los Angeles'
            },
            'ad_categories': ['sports']
        }
        result = process_bid_request(bid_request, self.targeting_criteria)
        self.assertEqual(result['bid_price'], 2.5)

    def test_wildcard_location_match(self):
        bid_request = {
            'request_id': 'req2',
            'user_id': 'user3',
            'device': 'desktop',
            'location': {
                'country': 'GB',
                'region': 'England',
                'city': 'London'
            },
            'ad_categories': ['technology']
        }
        result = process_bid_request(bid_request, self.targeting_criteria)
        self.assertEqual(result['bid_price'], 1.8)

    def test_no_match(self):
        bid_request = {
            'request_id': 'req3',
            'user_id': 'user3',
            'device': 'mobile',
            'location': {
                'country': 'FR',
                'region': 'Paris',
                'city': 'Paris'
            },
            'ad_categories': ['fashion']
        }
        result = process_bid_request(bid_request, self.targeting_criteria)
        self.assertEqual(result['bid_price'], 0.0)

    def test_empty_target_sets(self):
        bid_request = {
            'request_id': 'req4',
            'user_id': 'user4',
            'device': 'desktop',
            'location': {
                'country': 'JP',
                'region': 'Tokyo',
                'city': 'Tokyo'
            },
            'ad_categories': ['technology']
        }
        result = process_bid_request(bid_request, self.targeting_criteria)
        self.assertEqual(result['bid_price'], 1.8)

    def test_multiple_matches_highest_bid(self):
        # Add another criterion that would also match but with lower bid
        additional_criterion = {
            'criterion_id': 'crit3',
            'target_user_ids': {'user1'},
            'target_devices': {'mobile'},
            'target_locations': [
                {'country': 'US', 'region': 'California', 'city': 'Los Angeles'}
            ],
            'target_ad_categories': {'sports'},
            'bid_price': 1.0
        }
        criteria = self.targeting_criteria + [additional_criterion]
        
        bid_request = {
            'request_id': 'req5',
            'user_id': 'user1',
            'device': 'mobile',
            'location': {
                'country': 'US',
                'region': 'California',
                'city': 'Los Angeles'
            },
            'ad_categories': ['sports']
        }
        result = process_bid_request(bid_request, criteria)
        self.assertEqual(result['bid_price'], 2.5)

    def test_partial_category_match(self):
        bid_request = {
            'request_id': 'req6',
            'user_id': 'user1',
            'device': 'mobile',
            'location': {
                'country': 'US',
                'region': 'California',
                'city': 'Los Angeles'
            },
            'ad_categories': ['sports', 'technology']
        }
        result = process_bid_request(bid_request, self.targeting_criteria)
        self.assertEqual(result['bid_price'], 2.5)

if __name__ == '__main__':
    unittest.main()