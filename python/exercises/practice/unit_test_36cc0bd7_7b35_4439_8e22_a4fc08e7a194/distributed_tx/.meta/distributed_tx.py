def coordinate_transaction(transaction_id, transfers, server_mapping, commit_function, rollback_function):
    if not transfers:
        return True  # Empty transaction always succeeds

    # Validate all accounts exist in server mapping
    for transfer in transfers:
        source, destination, _ = transfer
        if source not in server_mapping or destination not in server_mapping:
            raise KeyError(f"Account not found in server mapping: {source if source not in server_mapping else destination}")

    # Group transfers by server
    server_transfers = {}
    for transfer in transfers:
        source, destination, amount = transfer
        source_server = server_mapping[source]
        dest_server = server_mapping[destination]

        # Add to source server's transfers
        if source_server not in server_transfers:
            server_transfers[source_server] = []
        server_transfers[source_server].append(('withdraw', source, amount))

        # Add to destination server's transfers
        if dest_server not in server_transfers:
            server_transfers[dest_server] = []
        server_transfers[dest_server].append(('deposit', destination, amount))

    # Prepare phase (implicit in this simplified version)
    # We directly attempt to commit since we're assuming servers are always prepared

    # Commit phase
    commit_success = commit_function(transaction_id, transfers)
    
    if commit_success:
        return True
    else:
        # Rollback phase
        rollback_success = rollback_function(transaction_id, transfers)
        if not rollback_success:
            raise RuntimeError("Failed to rollback transaction after commit failure")
        return False