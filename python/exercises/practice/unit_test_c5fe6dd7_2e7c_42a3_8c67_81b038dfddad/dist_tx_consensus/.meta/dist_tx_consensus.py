import time

def consensus(N, involved_nodes, coordinator_id, votes, timeout):
    start_time = time.time()
    # Coordinator initiates the request by gathering votes from all involved nodes.
    # In a real asynchronous distributed setting, the coordinator would wait for votes from each node
    # until the timeout expires. Here we simulate this behavior by checking for the presence of each vote.
    for node in involved_nodes:
        # Simulate waiting for a vote from the node until the timeout period.
        while node not in votes and time.time() - start_time < timeout:
            time.sleep(0.001)  # Sleep a bit to simulate waiting for a vote.
        # If vote is missing or vote is abort (False), then the consensus is abort.
        if not votes.get(node, False):
            return False
    # If all votes are commit, the consensus is commit.
    return True