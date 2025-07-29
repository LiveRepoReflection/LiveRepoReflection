def reconcile_data(nodes):
    """
    Reconcile conflicting data from multiple nodes using Last Write Wins strategy.
    
    Args:
        nodes: List of dictionaries, where each dictionary represents a node's state
               with keys mapping to {'value': int, 'timestamp': int} dictionaries
    
    Returns:
        Dictionary representing the final reconciled state
    
    Raises:
        ValueError: If any key-value pair is missing required fields or has invalid types
    """
    reconciled = {}
    
    for node in nodes:
        for key, data in node.items():
            # Validate data structure
            if not isinstance(data, dict):
                raise ValueError(f"Invalid data format for key '{key}'")
            if 'value' not in data or 'timestamp' not in data:
                raise ValueError(f"Missing required fields for key '{key}'")
            if not isinstance(data['value'], int) or not isinstance(data['timestamp'], int):
                raise ValueError(f"Invalid data types for key '{key}'")
            
            # Get existing entry if it exists
            existing = reconciled.get(key)
            
            # Update if:
            # 1. Key doesn't exist yet, or
            # 2. New timestamp is later, or
            # 3. Same timestamp but new value is smaller
            if (existing is None or 
                data['timestamp'] > existing['timestamp'] or
                (data['timestamp'] == existing['timestamp'] and 
                 data['value'] < existing['value'])):
                
                reconciled[key] = {
                    'value': data['value'],
                    'timestamp': data['timestamp']
                }
    
    # Convert to final format with just values
    return {k: v['value'] for k, v in reconciled.items()}