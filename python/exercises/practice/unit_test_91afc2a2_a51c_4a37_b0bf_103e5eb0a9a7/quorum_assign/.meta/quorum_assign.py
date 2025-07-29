def assign_quorums(N, K, transactions):
    """
    Assigns a write quorum for each transaction ensuring balanced load among nodes,
    minimized conflicts between consecutive transactions, and deterministic behavior.
    
    Parameters:
    - N (int): Number of nodes.
    - K (int): Quorum size.
    - transactions (list of int): List of transaction IDs.
    
    Returns:
    - list of tuples: Each tuple is (transaction_id, quorum) where quorum is a list of node IDs.
    """
    # Initialize load count for each node.
    load_counts = [0] * N
    result = []
    
    for idx, trans_id in enumerate(transactions):
        # Create a sorted list of nodes based on current load and adjusted ordering
        # The secondary key (node + idx) % N introduces a deterministic rotation to avoid conflicts.
        sorted_nodes = sorted(range(N), key=lambda node: (load_counts[node], (node + idx) % N))
        
        # Choose the first K nodes from sorted order as the quorum.
        quorum = sorted_nodes[:K]
        
        # Update the load count for each node used in the quorum.
        for node in quorum:
            load_counts[node] += 1
        
        result.append((trans_id, quorum))
    
    return result

if __name__ == "__main__":
    # Example usage:
    N = 5
    K = 3
    transactions = [101, 102, 103, 104, 105]
    assignments = assign_quorums(N, K, transactions)
    for trans_id, quorum in assignments:
        print(f"Transaction {trans_id}: Quorum {quorum}")