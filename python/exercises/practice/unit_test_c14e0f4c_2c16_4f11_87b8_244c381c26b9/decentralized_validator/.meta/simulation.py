import random

def simulate_network(nodes, transactions):
    for tx in transactions:
        # Randomly select a proposer
        proposer = random.choice(nodes)
        transaction_content = proposer.propose_transaction(tx)
        
        # Collect validation results
        validation_results = {}
        for node in nodes:
            is_valid = node.validate_transaction(
                transaction_content,
                node.get_global_state()
            )
            validation_results[node.node_id] = is_valid
        
        # Each node independently commits
        for node in nodes:
            node.commit_transaction(transaction_content, validation_results)
    
    # Return final states
    return {node.node_id: node.get_global_state() for node in nodes}