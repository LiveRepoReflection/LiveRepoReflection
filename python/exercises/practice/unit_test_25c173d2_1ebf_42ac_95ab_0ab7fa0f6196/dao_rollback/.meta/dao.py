def create_account(dao_state, account_id, initial_balance):
    if account_id in dao_state["accounts"]:
        return False
    dao_state["accounts"][account_id] = {"balance": initial_balance}
    return True

def create_proposal(dao_state, proposer_id, recipient_id, amount):
    return {
        "proposer_id": proposer_id,
        "recipient_id": recipient_id,
        "amount": amount,
        "votes": []
    }

def vote_on_proposal(proposal, voter_id):
    if voter_id not in proposal["votes"]:
        proposal["votes"].append(voter_id)

def create_block(dao_state, block_id, proposals):
    if block_id in dao_state["blocks"]:
        return False
    block = {
        "block_id": block_id,
        "proposals": proposals,
        "approvals": [],
        "snapshot": None
    }
    dao_state["blocks"][block_id] = block
    return block

def approve_block(block, approver_id):
    if approver_id not in block["approvals"]:
        block["approvals"].append(approver_id)

def _take_snapshot(dao_state):
    return {acc_id: acc["balance"] for acc_id, acc in dao_state["accounts"].items()}

def process_block(dao_state, block):
    # Take snapshot before processing
    block["snapshot"] = _take_snapshot(dao_state)
    
    total_accounts = len(dao_state["accounts"])
    required_votes = total_accounts // 2 + 1
    
    for proposal in block["proposals"]:
        # Check majority vote
        if len(proposal["votes"]) < required_votes:
            return False
        
        # Check accounts exist
        proposer_id = proposal["proposer_id"]
        recipient_id = proposal["recipient_id"]
        if (proposer_id not in dao_state["accounts"] or 
            recipient_id not in dao_state["accounts"]):
            return False
            
        # Check sufficient funds
        amount = proposal["amount"]
        if dao_state["accounts"][proposer_id]["balance"] < amount:
            return False
    
    # All checks passed, execute transactions
    for proposal in block["proposals"]:
        proposer_id = proposal["proposer_id"]
        recipient_id = proposal["recipient_id"]
        amount = proposal["amount"]
        
        dao_state["accounts"][proposer_id]["balance"] -= amount
        dao_state["accounts"][recipient_id]["balance"] += amount
    
    return True

def rollback_block(dao_state, block_id):
    if block_id not in dao_state["blocks"]:
        return False
    
    block = dao_state["blocks"][block_id]
    
    if block["snapshot"] is None:
        return False  # Block was never processed
    
    # Restore account balances from snapshot
    for acc_id, balance in block["snapshot"].items():
        if acc_id in dao_state["accounts"]:
            dao_state["accounts"][acc_id]["balance"] = balance
    
    # Remove the block
    del dao_state["blocks"][block_id]
    return True