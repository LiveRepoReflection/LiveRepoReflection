from collections import defaultdict
from enum import Enum, auto
from typing import Dict, List, Set, Tuple


class LogType(Enum):
    PREPARE = "PREPARE"
    VOTE_COMMIT = "VOTE_COMMIT"
    VOTE_ROLLBACK = "VOTE_ROLLBACK"
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"


class TransactionState(Enum):
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    INDETERMINATE = "INDETERMINATE"


def analyze_transaction_logs(logs: List[str]) -> Dict[str, str]:
    """
    Analyzes transaction logs and determines the final state of each transaction.
    
    Args:
        logs: A list of log entries in string format.
        
    Returns:
        A dictionary mapping transaction IDs to their final states.
    """
    # Parse logs
    parsed_logs = []
    for log in logs:
        try:
            parts = log.strip().split(',')
            if len(parts) < 4:
                raise ValueError(f"Invalid log format: {log}")
            
            node_id = int(parts[0])
            transaction_id = parts[1]
            try:
                log_type = LogType(parts[2])
            except ValueError:
                raise ValueError(f"Unknown log type '{parts[2]}' in log: {log}")
            
            timestamp = int(parts[3])
            data = parts[4] if len(parts) > 4 else ""
            
            parsed_logs.append((node_id, transaction_id, log_type, timestamp, data))
        except Exception as e:
            raise ValueError(f"Error parsing log: {log}. Error: {str(e)}")
    
    # Group logs by transaction
    transaction_logs = defaultdict(list)
    for log in parsed_logs:
        node_id, transaction_id, log_type, timestamp, data = log
        transaction_logs[transaction_id].append((node_id, log_type, timestamp, data))
    
    # Analyze each transaction
    results = {}
    for transaction_id, logs in transaction_logs.items():
        state = analyze_single_transaction(logs)
        results[transaction_id] = state.value
    
    return results


def analyze_single_transaction(logs: List[Tuple[int, LogType, int, str]]) -> TransactionState:
    """
    Analyzes logs for a single transaction and determines its final state.
    
    Args:
        logs: A list of log entries for a single transaction.
        
    Returns:
        The final state of the transaction.
    """
    # Track participating nodes and their states
    participating_nodes = set()
    prepared_nodes = set()
    voted_commit_nodes = set()
    voted_rollback_nodes = set()
    committed_nodes = set()
    rolled_back_nodes = set()
    
    # Process logs in chronological order
    sorted_logs = sorted(logs, key=lambda x: x[2])  # Sort by timestamp
    
    for node_id, log_type, timestamp, data in sorted_logs:
        participating_nodes.add(node_id)
        
        if log_type == LogType.PREPARE:
            prepared_nodes.add(node_id)
        elif log_type == LogType.VOTE_COMMIT:
            voted_commit_nodes.add(node_id)
        elif log_type == LogType.VOTE_ROLLBACK:
            voted_rollback_nodes.add(node_id)
        elif log_type == LogType.COMMIT:
            committed_nodes.add(node_id)
        elif log_type == LogType.ROLLBACK:
            rolled_back_nodes.add(node_id)
    
    # Analyze the state based on logs
    return determine_transaction_state(
        participating_nodes,
        prepared_nodes,
        voted_commit_nodes,
        voted_rollback_nodes,
        committed_nodes,
        rolled_back_nodes
    )


def determine_transaction_state(
    participating_nodes: Set[int],
    prepared_nodes: Set[int],
    voted_commit_nodes: Set[int],
    voted_rollback_nodes: Set[int],
    committed_nodes: Set[int],
    rolled_back_nodes: Set[int]
) -> TransactionState:
    """
    Determines the final state of a transaction based on the observed logs.
    
    Args:
        participating_nodes: Set of all nodes that participated in the transaction.
        prepared_nodes: Set of nodes that have a PREPARE log.
        voted_commit_nodes: Set of nodes that have a VOTE_COMMIT log.
        voted_rollback_nodes: Set of nodes that have a VOTE_ROLLBACK log.
        committed_nodes: Set of nodes that have a COMMIT log.
        rolled_back_nodes: Set of nodes that have a ROLLBACK log.
        
    Returns:
        The final state of the transaction.
    """
    # Check if all participating nodes have prepared
    if not all(node in prepared_nodes for node in participating_nodes):
        # There are nodes participating but not all have PREPARE logs
        return TransactionState.INDETERMINATE
    
    # If any node has committed and any node has rolled back, this is a protocol violation
    if committed_nodes and rolled_back_nodes:
        return TransactionState.INDETERMINATE
    
    # If all participating nodes have committed, the transaction is committed
    if committed_nodes and committed_nodes == participating_nodes:
        return TransactionState.COMMITTED
    
    # If any node has rolled back, the transaction is rolled back
    if rolled_back_nodes:
        return TransactionState.ROLLED_BACK
    
    # If there are any vote rollbacks, it should lead to rollback decision
    # But we haven't seen a rollback log, so it's indeterminate
    if voted_rollback_nodes:
        return TransactionState.INDETERMINATE
    
    # If we've seen votes to commit from all nodes but not all commit logs,
    # it's indeterminate
    if voted_commit_nodes == participating_nodes and committed_nodes != participating_nodes:
        return TransactionState.INDETERMINATE
    
    # Default to indeterminate for any other case
    return TransactionState.INDETERMINATE