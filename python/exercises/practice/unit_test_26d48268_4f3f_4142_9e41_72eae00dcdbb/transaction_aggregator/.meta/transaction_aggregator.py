import bisect
import time
from collections import defaultdict
from typing import Dict, List, Tuple, Any


class TransactionAggregator:
    def __init__(self):
        """
        Initialize the TransactionAggregator with necessary data structures.
        We'll use a time-segmented approach for efficient time window queries.
        """
        # Main storage for transactions by category
        # Structure: {category: [(timestamp, amount, user_id), ...]}
        self.transactions_by_category = defaultdict(list)
        
        # User transaction amounts by category and timestamp
        # Structure: {category: {user_id: [(timestamp, amount), ...]}}
        self.user_transactions = defaultdict(lambda: defaultdict(list))
        
        # Cached aggregations for common time windows
        # Structure: {category: {time_window: {"total": amount, "top_users": [(user_id, amount), ...]}}}
        self.cache = defaultdict(dict)
        
        # Cache expiration timestamp
        self.cache_expiry = {}

    def add_transaction(self, transaction: Dict[str, Any]) -> None:
        """
        Add a new transaction to the aggregator.
        
        Args:
            transaction: A dictionary containing transaction data
        """
        transaction_id = transaction["transaction_id"]
        timestamp = transaction["timestamp"]
        amount = transaction["amount"]
        category = transaction["category"]
        user_id = transaction["user_id"]
        
        # Store transaction in sorted order by timestamp
        transaction_record = (timestamp, amount, user_id)
        # Use binary search to find the correct insertion position
        pos = bisect.bisect_left([t[0] for t in self.transactions_by_category[category]], timestamp)
        self.transactions_by_category[category].insert(pos, transaction_record)
        
        # Store user transaction
        user_trans = (timestamp, amount)
        pos = bisect.bisect_left([t[0] for t in self.user_transactions[category][user_id]], timestamp)
        self.user_transactions[category][user_id].insert(pos, user_trans)
        
        # Invalidate affected cache entries
        # In a production system, we'd be more selective about which cache entries to invalidate
        self._invalidate_cache_for_category(category)

    def get_total_by_category(self, category: str, start_time: int, end_time: int) -> float:
        """
        Get total transaction amount for a category within a time window.
        
        Args:
            category: The transaction category
            start_time: Start timestamp (inclusive)
            end_time: End timestamp (inclusive)
            
        Returns:
            Total transaction amount
        """
        cache_key = (start_time, end_time)
        
        # Check if we have a cached result and it's still valid
        if cache_key in self.cache[category] and self.cache_expiry.get(category, 0) > time.time():
            return self.cache[category][cache_key]["total"]
        
        transactions = self.transactions_by_category.get(category, [])
        if not transactions:
            return 0
        
        # Find index range for the time window using binary search
        start_idx = bisect.bisect_left([t[0] for t in transactions], start_time)
        end_idx = bisect.bisect_right([t[0] for t in transactions], end_time)
        
        # Calculate total
        total = sum(t[1] for t in transactions[start_idx:end_idx])
        
        # Cache the result
        if end_time < int(time.time()):  # Only cache historical queries
            if cache_key not in self.cache[category]:
                self.cache[category][cache_key] = {}
            self.cache[category][cache_key]["total"] = total
            self.cache_expiry[category] = time.time() + 300  # Cache for 5 minutes
            
        return total

    def get_top_users_by_category(self, category: str, start_time: int, end_time: int, k: int) -> List[Tuple[int, float]]:
        """
        Get top K users by transaction amount for a category within a time window.
        
        Args:
            category: The transaction category
            start_time: Start timestamp (inclusive)
            end_time: End timestamp (inclusive)
            k: Number of top users to return
            
        Returns:
            List of (user_id, total_amount) tuples, sorted by total_amount in descending order
        """
        cache_key = (start_time, end_time, k)
        
        # Check if we have a cached result and it's still valid
        if cache_key in self.cache[category] and self.cache_expiry.get(category, 0) > time.time():
            return self.cache[category][cache_key]["top_users"]
        
        if category not in self.user_transactions:
            return []
        
        # Calculate total amount per user within the time window
        user_totals = {}
        for user_id, transactions in self.user_transactions[category].items():
            # Skip binary search if the user has few transactions (optimization for small lists)
            if len(transactions) <= 10:
                user_total = sum(amount for ts, amount in transactions if start_time <= ts <= end_time)
            else:
                # Binary search to find range
                start_idx = bisect.bisect_left([t[0] for t in transactions], start_time)
                end_idx = bisect.bisect_right([t[0] for t in transactions], end_time)
                user_total = sum(t[1] for t in transactions[start_idx:end_idx])
            
            if user_total > 0:
                user_totals[user_id] = user_total
        
        # Sort and get top K
        top_users = sorted(user_totals.items(), key=lambda x: x[1], reverse=True)[:k]
        
        # Cache the result
        if end_time < int(time.time()):  # Only cache historical queries
            if cache_key not in self.cache[category]:
                self.cache[category][cache_key] = {}
            self.cache[category][cache_key]["top_users"] = top_users
            self.cache_expiry[category] = time.time() + 300  # Cache for 5 minutes
            
        return top_users

    def _invalidate_cache_for_category(self, category: str) -> None:
        """
        Invalidate all cache entries for a specific category.
        
        Args:
            category: The category to invalidate cache for
        """
        self.cache.pop(category, None)
        self.cache_expiry.pop(category, None)

    def cleanup_old_transactions(self, cutoff_time: int) -> None:
        """
        Remove transactions older than cutoff_time to save memory.
        
        Args:
            cutoff_time: Timestamp before which transactions will be removed
        """
        for category, transactions in self.transactions_by_category.items():
            if not transactions:
                continue
                
            # Find index of first transaction that's newer than cutoff
            idx = bisect.bisect_left([t[0] for t in transactions], cutoff_time)
            if idx > 0:
                self.transactions_by_category[category] = transactions[idx:]
        
        # Clean up user transactions
        for category, users in self.user_transactions.items():
            for user_id, transactions in list(users.items()):
                idx = bisect.bisect_left([t[0] for t in transactions], cutoff_time)
                if idx > 0:
                    self.user_transactions[category][user_id] = transactions[idx:]
                # Remove user if they have no transactions left
                if not self.user_transactions[category][user_id]:
                    del self.user_transactions[category][user_id]
            
            # Remove category if it has no users left
            if not self.user_transactions[category]:
                del self.user_transactions[category]
        
        # Invalidate all cache since we removed data
        self.cache.clear()
        self.cache_expiry.clear()