class Auction:
    def __init__(self, item_id, seller_id, start_block, duration, blockchain):
        if not isinstance(item_id, str) or not isinstance(seller_id, str):
            raise ValueError("item_id and seller_id must be strings")
        if not (isinstance(start_block, int) and isinstance(duration, int)) or start_block <= 0 or duration <= 0:
            raise ValueError("start_block and duration must be positive integers")
        self.item_id = item_id
        self.seller_id = seller_id
        self.start_block = start_block
        self.duration = duration
        self.blockchain = blockchain
        self.bids = []
        self.highest_bid = 0
        self.highest_bidder = None
        self.settled = False

    def place_bid(self, bidder_id, bid_amount, current_block):
        # Check if the auction is within the valid bidding window.
        if current_block < self.start_block or current_block >= self.start_block + self.duration:
            return False
        # Validate bid_amount: must be a positive integer.
        if not isinstance(bid_amount, int) or bid_amount <= 0:
            return False
        # Prevent the seller from bidding.
        if bidder_id == self.seller_id:
            return False
        # Ensure the bid is strictly greater than the current highest bid.
        if bid_amount <= self.highest_bid:
            return False

        # Update auction with the new bid.
        self.highest_bid = bid_amount
        self.highest_bidder = bidder_id
        self.bids.append((bidder_id, bid_amount))

        # Record the bid as a transaction in the blockchain.
        tx_data = {
            'type': 'bid',
            'auction_id': self.item_id,
            'bidder_id': bidder_id,
            'bid_amount': bid_amount
        }
        transaction = Transaction(tx_data)
        if hasattr(self.blockchain, "add_transaction_to_current_block"):
            self.blockchain.add_transaction_to_current_block(transaction)
        return True

    def settle_auction(self, current_block):
        # Auction can only be settled after its duration has elapsed.
        if current_block < self.start_block + self.duration:
            return False
        # Cannot settle an auction that is already settled.
        if self.settled:
            return False
        # There must be at least one bid to settle the auction.
        if self.highest_bidder is None:
            return False

        self.settled = True
        tx_data = {
            'type': 'settlement',
            'auction_id': self.item_id,
            'seller_id': self.seller_id,
            'highest_bidder': self.highest_bidder,
            'bid_amount': self.highest_bid
        }
        transaction = Transaction(tx_data)
        if hasattr(self.blockchain, "add_transaction_to_current_block"):
            self.blockchain.add_transaction_to_current_block(transaction)
        return True


class Transaction:
    def __init__(self, data):
        self.data = data