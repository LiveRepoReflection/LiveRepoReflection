from copy import deepcopy
from typing import Dict, List, Any

def validate_transaction(service_state: Dict[str, Dict[str, int]], 
                       transaction_log: List[Dict[str, Any]]) -> bool:
    """
    Validates a transaction log against the given service state.
    Returns True if the transaction is valid, False otherwise.
    """
    # Create a working copy of the service state to apply changes
    current_state = deepcopy(service_state)
    
    # Handle empty transaction log case
    if not transaction_log:
        return True
    
    # Process each operation in the transaction log
    for operation in transaction_log:
        service_id = operation['service_id']
        operation_type = operation['operation_type']
        data_id = operation['data_id']
        
        # Ensure service exists for non-create operations
        if service_id not in current_state:
            if operation_type != 'create':
                return False
            current_state[service_id] = {}
            
        service_data = current_state[service_id]
        
        # Validate and apply operation based on type
        if operation_type == 'update':
            if (data_id not in service_data or 
                service_data[data_id] != operation['expected_value']):
                return False
            service_data[data_id] = operation['new_value']
            
        elif operation_type == 'delete':
            if (data_id not in service_data or 
                service_data[data_id] != operation['expected_value']):
                return False
            del service_data[data_id]
            
        elif operation_type == 'create':
            if data_id in service_data:
                return False
            service_data[data_id] = operation['new_value']
            
        else:
            # Invalid operation type
            return False
            
    return True