import unittest
from auction_consensus import decentralized_auction

class TestAuctionConsensus(unittest.TestCase):
    def test_single_bid(self):
        bids = [100]
        k = 1
        f = 0
        result = decentralized_auction(bids, k, f)
        self.assertEqual(result, 100, "With one bid, it should return that bid.")

    def test_no_byzantine(self):
        # In the absence of Byzantine faults (f = 0),
        # the kth highest bid must be exactly the kth element from the sorted order.
        bids = [120, 90, 100, 80]
        k = 1
        f = 0
        expected = sorted(bids, reverse=True)[k-1]  # highest bid
        result = decentralized_auction(bids, k, f)
        self.assertEqual(result, expected, "When there are no Byzantine faults, the kth highest bid must match the sorted order.")

    def test_duplicates(self):
        # All bids are the same. Regardless of k and f, answer should be that bid.
        bids = [100, 100, 100, 100]
        k = 2
        f = 1  # even if we allow faults, all values are identical.
        result = decentralized_auction(bids, k, f)
        self.assertEqual(result, 100, "All bids identical should return that bid.")

    def test_all_identical(self):
        # Another test with all items identical.
        bids = [50, 50, 50, 50, 50]
        k = 3
        f = 0
        result = decentralized_auction(bids, k, f)
        self.assertEqual(result, 50, "All identical bids must return the same value.")

    def test_example_with_byzantine(self):
        # This test corresponds to the provided example:
        # bids include an extreme outlier that is likely from a Byzantine node.
        bids = [100, 50, 75, 120, 90, 50, 110, 60, 80, 1000]
        k = 3
        f = 1
        # According to the problem description, a correct solution might ignore the malicious bid.
        # Acceptable outputs are either 90 or 100.
        result = decentralized_auction(bids, k, f)
        self.assertIn(result, {90, 100}, "For the example, the kth highest benign bid should be either 90 or 100.")

    def test_valid_byzantine_removal(self):
        # Create a scenario with clear benign bids and malicious outliers.
        good_bids = [100, 95, 90, 85, 80]
        malicious_bids = [1000, 1000]  # clearly outlying bids
        bids = good_bids + malicious_bids
        k = 3
        # With f = 2, the algorithm should mitigate the malicious impact and choose from the good bids.
        # The 3rd highest from good_bids is 90.
        f = 2
        result = decentralized_auction(bids, k, f)
        self.assertEqual(result, 90, "The kth highest bid should be 90 after mitigating malicious bids.")

    def test_large_input(self):
        # Test performance and correctness on a larger randomized input.
        import random
        random.seed(42)
        # Generate a list of bids:
        good_bids = [random.randint(50, 150) for _ in range(1000)]
        # Introduce a few malicious bids that are extreme.
        malicious_bids = [10**6] * 200  # 200 Byzantine bids
        bids = good_bids + malicious_bids
        k = 500  # choose a middle rank
        f = 150   # allowed Byzantine count is less than len(bids)/3 (which is 400 here)
        result = decentralized_auction(bids, k, f)
        # Must return a bid that was present in the original list.
        self.assertIn(result, bids, "The result must be one of the submitted bids.")
        # For f == 0, kth highest from good_bids would be:
        # However, when Byzantine bids are present, the algorithm is expected to mitigate them.
        # Thus, we only check that the result comes from the set of bids.
        
if __name__ == '__main__':
    unittest.main()