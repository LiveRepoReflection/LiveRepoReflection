import random

def coordinate_transaction(services, transaction):
    """
    Implements a distributed transaction coordinator using the Saga pattern.
    
    Args:
        services (dict): Dictionary of services where key is service_id and value is a list [perform_function, compensate_function]
        transaction (list): List of tuples (service_id, operation_data) representing the operations to be performed
        
    Returns:
        tuple: (success_flag, logs)
            - success_flag (bool): True if transaction committed successfully, False otherwise
            - logs (list): List of strings representing logs of actions taken
    """
    logs = []
    successful_operations = []  # Track successful operations for compensation
    
    # Execute each operation in the transaction
    for service_id, operation_data in transaction:
        perform_function = services[service_id][0]
        success = perform_function(operation_data)
        
        # Log the perform operation result
        status = "success" if success else "failure"
        log_entry = f"perform: service_{service_id} with data '{operation_data}' - {status}"
        logs.append(log_entry)
        
        if success:
            # If operation succeeded, add to successful_operations for potential compensation
            successful_operations.append((service_id, operation_data))
        else:
            # If operation failed, trigger compensation for all successful operations in reverse order
            for comp_service_id, comp_operation_data in reversed(successful_operations):
                compensate_function = services[comp_service_id][1]
                comp_success = compensate_function(comp_operation_data)
                
                # Log the compensate operation result
                comp_status = "success" if comp_success else "failure"
                comp_log_entry = f"compensate: service_{comp_service_id} with data '{comp_operation_data}' - {comp_status}"
                logs.append(comp_log_entry)
                
                # Note: We continue compensation even if a compensate operation fails
            
            # Return False since transaction failed and was rolled back
            return False, logs
    
    # If we reach this point, all operations succeeded
    return True, logs