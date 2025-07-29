import unittest

# Dummy implementations for Blockchain, Block, and Transaction for testing purposes.

class Transaction:
    def __init__(self, data):
        self.data = data

class Block:
    def __init__(self, block_number):
        self.block_number = block_number
        self.transactions = []
    
    def add_transaction(self, transaction):
        self.transactions.append(transaction)

class Blockchain:
    def __init__(self):
        self.blocks = []
        self.current_block_number = 0
        # Initialize the first block.
        self.add_new_block()
    
    def add_new_block(self):
        block = Block(self.current_block_number)
        self.blocks.append(block)
        self.current_block_number += 1
    
    def get_current_block_height(self):
        # Return the current block number (the number of the most recently added block)
        return self.blocks[-1].block_number
    
    def add_transaction_to_current_block(self, transaction):
        self.blocks[-1].add_transaction(transaction)

# For testing, we simulate the Auction class behavior with a wrapper that uses the dummy blockchain.
# The Auction class is assumed to be defined in the decentralized_auction module.
# Here we import it.
from decentralized_auction import Auction

class TestDecentralizedAuction(unittest.TestCase):
    def setUp(self):
        self.blockchain = Blockchain()
        # We'll start the auction at block 2 and set duration to 5 blocks (auction runs blocks 2,3,4,5,6)
        self.auction = Auction("item_001", "Alice", 2, 5, self.blockchain)
    
    def test_place_valid_bid(self):
        # Move to block 2 to start the auction.
        self._advance_blocks(to_block=2)
        current_block = self.blockchain.get_current_block_height()
        # Valid bid by Bob
        result = self.auction.place_bid("Bob", 100, current_block)
        self.assertTrue(result)
        self.assertEqual(self.auction.highest_bid, 100)
        self.assertEqual(self.auction.highest_bidder, "Bob")
        # Check that a transaction has been added
        tx_found = self._find_transaction_in_block(current_block, 
            {'type': 'bid', 'auction_id': self.auction.item_id, 'bidder_id': "Bob", 'bid_amount': 100})
        self.assertTrue(tx_found)
    
    def test_bid_lower_than_current(self):
        self._advance_blocks(to_block=2)
        current_block = self.blockchain.get_current_block_height()
        # First valid bid by Bob
        result = self.auction.place_bid("Bob", 150, current_block)
        self.assertTrue(result)
        # Advance block for next bid
        self.blockchain.add_new_block()
        current_block = self.blockchain.get_current_block_height()
        # Second bid by Charlie with lower bid amount
        result = self.auction.place_bid("Charlie", 120, current_block)
        self.assertFalse(result)
        # Highest bid remains unchanged
        self.assertEqual(self.auction.highest_bid, 150)
        self.assertEqual(self.auction.highest_bidder, "Bob")
    
    def test_bid_by_seller_rejected(self):
        self._advance_blocks(to_block=2)
        current_block = self.blockchain.get_current_block_height()
        # Seller (Alice) attempts to bid
        result = self.auction.place_bid("Alice", 200, current_block)
        self.assertFalse(result)
        # No changes to highest bid
        self.assertIsNone(self.auction.highest_bidder)
        self.assertEqual(self.auction.highest_bid, 0)
    
    def test_bid_outside_auction_time(self):
        # Attempt bid before auction start.
        current_block = self.blockchain.get_current_block_height()  # Initially block 0 or 1
        result = self.auction.place_bid("Bob", 100, current_block)
        self.assertFalse(result)
        # Move to after auction end
        self._advance_blocks(to_block=self.auction.start_block + self.auction.duration)
        current_block = self.blockchain.get_current_block_height()
        result = self.auction.place_bid("Charlie", 200, current_block)
        self.assertFalse(result)
    
    def test_settle_auction_before_end(self):
        # Place a valid bid then attempt to settle before auction end.
        self._advance_blocks(to_block=2)
        current_block = self.blockchain.get_current_block_height()
        self.auction.place_bid("Bob", 150, current_block)
        # Try settling before auction duration is over.
        settle_result = self.auction.settle_auction(current_block)
        self.assertFalse(settle_result)
    
    def test_settle_auction_no_bid(self):
        # Advance to auction end with no bids.
        self._advance_blocks(to_block=self.auction.start_block + self.auction.duration)
        current_block = self.blockchain.get_current_block_height()
        settle_result = self.auction.settle_auction(current_block)
        self.assertFalse(settle_result)
    
    def test_successful_settlement(self):
        # Place bids and then settle after auction ends.
        self._advance_blocks(to_block=2)
        current_block = self.blockchain.get_current_block_height()
        self.auction.place_bid("Bob", 100, current_block)
        self.blockchain.add_new_block()
        current_block = self.blockchain.get_current_block_height()
        self.auction.place_bid("Charlie", 200, current_block)
        # Advance blocks to beyond auction duration.
        self._advance_blocks(to_block=self.auction.start_block + self.auction.duration)
        current_block = self.blockchain.get_current_block_height()
        settle_result = self.auction.settle_auction(current_block)
        self.assertTrue(settle_result)
        self.assertTrue(self.auction.settled)
        # Check that settlement transaction is recorded in the current block
        tx_found = self._find_transaction_in_block(current_block,
            {'type': 'settlement', 'auction_id': self.auction.item_id, 'seller_id': "Alice",
             'highest_bidder': "Charlie", 'bid_amount': 200})
        self.assertTrue(tx_found)
    
    def test_settle_twice(self):
        # Place a valid bid.
        self._advance_blocks(to_block=2)
        current_block = self.blockchain.get_current_block_height()
        self.auction.place_bid("Bob", 100, current_block)
        # Advance to end and settle.
        self._advance_blocks(to_block=self.auction.start_block + self.auction.duration)
        current_block = self.blockchain.get_current_block_height()
        first_settle = self.auction.settle_auction(current_block)
        self.assertTrue(first_settle)
        # Attempt to settle a second time
        second_settle = self.auction.settle_auction(current_block)
        self.assertFalse(second_settle)
    
    def test_no_bidding_after_settlement(self):
        # Place bid and settle auction
        self._advance_blocks(to_block=2)
        current_block = self.blockchain.get_current_block_height()
        self.auction.place_bid("Bob", 100, current_block)
        self._advance_blocks(to_block=self.auction.start_block + self.auction.duration)
        current_block = self.blockchain.get_current_block_height()
        self.auction.settle_auction(current_block)
        # Attempt to place a bid after settlement
        self.blockchain.add_new_block()
        current_block = self.blockchain.get_current_block_height()
        result = self.auction.place_bid("Charlie", 150, current_block)
        self.assertFalse(result)
    
    def _advance_blocks(self, to_block):
        """
        Helper method to advance the blockchain until the current block height reaches `to_block`.
        """
        while self.blockchain.get_current_block_height() < to_block:
            self.blockchain.add_new_block()
    
    def _find_transaction_in_block(self, block_number, expected_data):
        """
        Helper method to search for a transaction with matching data in a given block.
        Returns True if found, False otherwise.
        """
        # Find the block with block_number.
        for block in self.blockchain.blocks:
            if block.block_number == block_number:
                for tx in block.transactions:
                    if tx.data == expected_data:
                        return True
        return False

if __name__ == '__main__':
    unittest.main()