## Project Name

`Decentralized Auction House`

## Question Description

You are tasked with building the core logic for a decentralized auction house. This auction house will operate on a simplified blockchain environment. The goal is to implement the key functionalities of placing bids, determining the winner, and distributing assets, while adhering to blockchain principles such as immutability and transparency.

**Auction Structure:**

Each auction runs for a fixed duration (in blocks). An auction is initiated with a specific item being offered for sale. Users can place bids during the auction period.  At the end of the auction, the highest bidder wins the item, and their bid amount is transferred to the seller.

**Simplified Blockchain Environment:**

Assume the existence of the following:

*   **`Blockchain` Class:** This class simulates a blockchain. It manages a list of `Block` objects. It has methods to add new blocks and retrieve the current block height (block number). You don't need to implement this class, it will be provided for testing.
*   **`Block` Class:**  Represents a block in the blockchain.  Each block contains a list of `Transaction` objects. It also contains the block number. You don't need to implement this class, it will be provided for testing.
*   **`Transaction` Class:** Represents a transaction on the blockchain.  For this problem, a transaction will be either a bid placement or the final settlement of the auction. You don't need to implement this class, it will be provided for testing.
*   **`Auction` Class:** Represents an individual auction. You will implement this class.

**Your Task:**

Implement the `Auction` class with the following functionalities:

1.  **`__init__(self, item_id, seller_id, start_block, duration, blockchain)`:**
    *   Initializes the auction with the `item_id` being auctioned, the `seller_id` of the seller, the `start_block` when the auction begins, the `duration` of the auction in blocks, and a reference to the `blockchain` object.
    *   Maintains a list of `bids` (a list of tuples: `(bidder_id, bid_amount)`).
    *   Stores the current `highest_bidder` and `highest_bid`. Initially, these should be `None` and 0 respectively.
    *   Stores the `settled` status, initially `False`.

2.  **`place_bid(self, bidder_id, bid_amount, current_block)`:**
    *   Places a bid on the auction.
    *   The bid should only be accepted if:
        *   The auction is still running (`current_block` is within the auction's timeframe: `start_block <= current_block < start_block + duration`).
        *   The bid amount is strictly greater than the current `highest_bid`.
        *   The `bidder_id` is not the same as `seller_id`.
    *   If the bid is accepted:
        *   Update the `highest_bidder` and `highest_bid` with the new values.
        *   Append the bid to the `bids` list.
        *   Return `True`.
    *   If the bid is rejected, return `False`.
    *   Each bid placement must be recorded as a new `Transaction` in the current block of the `blockchain`. The transaction's data field should contain a dictionary of the form: `{'type': 'bid', 'auction_id': self.item_id, 'bidder_id': bidder_id, 'bid_amount': bid_amount}`.

3.  **`settle_auction(self, current_block)`:**
    *   Settles the auction.
    *   The auction should only be settled if:
        *   The auction is over (`current_block >= start_block + duration`).
        *   The auction has not already been settled (`self.settled` is `False`).
        *   There is at least one bid (highest_bidder is not None).
    *   If the auction is settled:
        *   Set `self.settled` to `True`.
        *   Create a transaction to transfer the `highest_bid` amount from the `highest_bidder` to the `seller_id`. The transaction's data field should be a dictionary of the form: `{'type': 'settlement', 'auction_id': self.item_id, 'seller_id': self.seller_id, 'highest_bidder': self.highest_bidder, 'bid_amount': self.highest_bid}`.
        *   Add the transaction to the current block of the `blockchain`.
        *   Return `True`.
    *   If the auction cannot be settled, return `False`.

**Constraints:**

*   All bid amounts must be positive integers.
*   The `item_id`, `seller_id`, and `bidder_id` are strings.
*   The `start_block` and `duration` are positive integers.
*   Optimize the `place_bid` and `settle_auction` methods for efficiency.  Avoid unnecessary iterations or computations.  Consider the performance impact as the number of bids increases.

**Example Usage (Illustrative - actual Blockchain/Block/Transaction classes will be provided):**

```python
# Assume Blockchain, Block, and Transaction classes are defined elsewhere.
blockchain = Blockchain()
auction = Auction("NFT_001", "Alice", 5, 10, blockchain)  # Item, Seller, Start Block, Duration, Blockchain

blockchain.add_new_block() # Block 5
auction.place_bid("Bob", 100, blockchain.get_current_block_height()) # True
blockchain.add_new_block() # Block 6
auction.place_bid("Charlie", 150, blockchain.get_current_block_height()) # True
blockchain.add_new_block() # Block 7
auction.place_bid("David", 120, blockchain.get_current_block_height()) # False (lower than highest bid)

# ... more blocks and bids ...

blockchain.add_new_block() # Block 15
auction.settle_auction(blockchain.get_current_block_height()) # True, transfers 150 from Charlie to Alice

# Further attempts to bid or settle after the auction ends should fail.
blockchain.add_new_block() # Block 16
auction.place_bid("Eve", 200, blockchain.get_current_block_height()) # False
auction.settle_auction(blockchain.get_current_block_height()) # False (already settled)
```

**Scoring:**

Your solution will be evaluated on:

*   **Correctness:** Does your code implement the auction logic accurately according to the specifications and constraints?
*   **Efficiency:** Is your code optimized for performance, especially with a large number of bids?
*   **Code Quality:** Is your code well-structured, readable, and maintainable?  Does it adhere to Python best practices?
*   **Edge Cases:** Does your code handle all edge cases correctly, such as invalid bids, attempts to settle the auction prematurely, and auctions with no bids?
