from collections import defaultdict

def can_serialize_transactions(num_nodes, transactions):
    """
    Determines if there exists a serializable execution order for the given transactions.
    Uses a graph-based approach to detect cycles in transaction dependencies.
    
    Args:
        num_nodes: Number of nodes in the system
        transactions: List of tuples (node_id, read_items, write_items)
    
    Returns:
        bool: True if a serializable order exists, False otherwise
    """
    if not transactions:
        return True

    # Create a graph where vertices are transaction indices
    # and edges represent dependencies between transactions
    graph = defaultdict(set)
    
    # Create write_map to track which transaction writes which data item
    write_map = {}  # data_item -> transaction_index
    
    # First pass: Record all writes
    for i, (_, _, write_items) in enumerate(transactions):
        for item in write_items:
            if item in write_map:
                # Multiple transactions trying to write to same item
                return False
            write_map[item] = i

    # Second pass: Build dependency graph
    for i, (_, read_items, write_items) in enumerate(transactions):
        # Read-Write conflicts (WR dependencies)
        for item in read_items:
            if item in write_map and write_map[item] != i:
                writer = write_map[item]
                graph[writer].add(i)
                
        # Write-Read conflicts (RW dependencies)
        for item in write_items:
            for j, (_, other_reads, _) in enumerate(transactions):
                if i != j and item in other_reads:
                    graph[i].add(j)
                    
        # Write-Write conflicts (WW dependencies)
        for item in write_items:
            if item in read_items:
                # If a transaction reads and writes the same item,
                # it might create a cycle with other transactions
                for j, (_, other_reads, _) in enumerate(transactions):
                    if i != j and item in other_reads:
                        return False

    # Detect cycles using DFS
    def has_cycle(vertex, visited, rec_stack):
        visited[vertex] = True
        rec_stack[vertex] = True
        
        for neighbor in graph[vertex]:
            if not visited[neighbor]:
                if has_cycle(neighbor, visited, rec_stack):
                    return True
            elif rec_stack[neighbor]:
                return True
                
        rec_stack[vertex] = False
        return False

    # Check for cycles
    visited = [False] * len(transactions)
    rec_stack = [False] * len(transactions)
    
    for i in range(len(transactions)):
        if not visited[i]:
            if has_cycle(i, visited, rec_stack):
                return False

    return True