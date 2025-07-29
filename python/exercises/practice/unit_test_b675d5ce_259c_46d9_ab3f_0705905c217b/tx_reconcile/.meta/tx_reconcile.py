from decimal import Decimal
from typing import List, Dict, Optional, Any, Union
from collections import defaultdict

def reconcile_transactions(
    expected_transactions: List[Dict[str, Any]],
    observed_transactions: List[Dict[str, Any]],
    time_window: int,
    amount_tolerance: Decimal
) -> List[Dict[str, Any]]:
    """
    Reconcile transactions between expected and observed transaction streams.
    
    Args:
        expected_transactions: List of expected transaction records.
        observed_transactions: List of observed transaction records.
        time_window: Time window (in seconds) within which transactions are considered matching.
        amount_tolerance: Tolerance for amount differences.
        
    Returns:
        List of discrepancy records.
    """
    discrepancies = []
    
    # Create indexes for efficient lookup
    expected_by_id = {}
    observed_by_id = defaultdict(list)
    
    # Index expected transactions by ID
    for tx in expected_transactions:
        expected_by_id[tx["transaction_id"]] = tx
    
    # Index observed transactions by ID (could have multiple with same ID but different timestamps)
    for tx in observed_transactions:
        observed_by_id[tx["transaction_id"]].append(tx)
    
    # Track processed observed transactions to identify unexpected ones
    processed_observed_txs = set()
    
    # Check each expected transaction
    for expected_tx in expected_transactions:
        tx_id = expected_tx["transaction_id"]
        expected_timestamp = expected_tx["timestamp"]
        
        # Find matching observed transactions within time window
        matching_observed = []
        if tx_id in observed_by_id:
            for observed_tx in observed_by_id[tx_id]:
                observed_timestamp = observed_tx["timestamp"]
                if abs(observed_timestamp - expected_timestamp) <= time_window:
                    matching_observed.append(observed_tx)
        
        if not matching_observed:
            # Missing transaction
            discrepancies.append({
                "discrepancy_type": "Missing",
                "transaction_id": tx_id,
                "expected_record": expected_tx,
                "observed_record": None,
                "details": f"Transaction {tx_id} is missing in observed transactions"
            })
        else:
            # We found at least one matching transaction within the time window
            # For simplicity, we'll use the one with the closest timestamp
            matching_observed.sort(key=lambda tx: abs(tx["timestamp"] - expected_timestamp))
            observed_tx = matching_observed[0]
            
            # Mark as processed
            processed_observed_txs.add(id(observed_tx))
            
            # Check for mismatches
            # Amount mismatch
            if abs(expected_tx["amount"] - observed_tx["amount"]) > amount_tolerance:
                discrepancies.append({
                    "discrepancy_type": "AmountMismatch",
                    "transaction_id": tx_id,
                    "expected_record": expected_tx,
                    "observed_record": observed_tx,
                    "details": f"Expected amount: {expected_tx['amount']}, Observed amount: {observed_tx['amount']}"
                })
            
            # Currency mismatch
            if expected_tx["currency"] != observed_tx["currency"]:
                discrepancies.append({
                    "discrepancy_type": "CurrencyMismatch",
                    "transaction_id": tx_id,
                    "expected_record": expected_tx,
                    "observed_record": observed_tx,
                    "details": f"Expected currency: {expected_tx['currency']}, Observed currency: {observed_tx['currency']}"
                })
            
            # Type mismatch
            if expected_tx["type"] != observed_tx["type"]:
                discrepancies.append({
                    "discrepancy_type": "TypeMismatch",
                    "transaction_id": tx_id,
                    "expected_record": expected_tx,
                    "observed_record": observed_tx,
                    "details": f"Expected type: {expected_tx['type']}, Observed type: {observed_tx['type']}"
                })
    
    # Check for unexpected transactions
    for observed_tx_list in observed_by_id.values():
        for observed_tx in observed_tx_list:
            # Skip if we've already processed this transaction
            if id(observed_tx) in processed_observed_txs:
                continue
                
            tx_id = observed_tx["transaction_id"]
            observed_timestamp = observed_tx["timestamp"]
            
            # Check if there's a matching expected transaction outside the time window
            if tx_id in expected_by_id:
                expected_timestamp = expected_by_id[tx_id]["timestamp"]
                if abs(observed_timestamp - expected_timestamp) > time_window:
                    # This is unexpected because it's outside the time window
                    discrepancies.append({
                        "discrepancy_type": "Unexpected",
                        "transaction_id": tx_id,
                        "expected_record": None,
                        "observed_record": observed_tx,
                        "details": f"Transaction {tx_id} is unexpected in observed transactions"
                    })
            else:
                # This transaction was not expected at all
                discrepancies.append({
                    "discrepancy_type": "Unexpected",
                    "transaction_id": tx_id,
                    "expected_record": None,
                    "observed_record": observed_tx,
                    "details": f"Transaction {tx_id} is unexpected in observed transactions"
                })
    
    return discrepancies