import math

def evaluate_proposal(
    N, edges, node_performances, node_dependencies,
    proposal, votes, total_tokens, quorum_threshold,
    approval_threshold, influence_factor, critical_threshold
):
    # Check voting requirements
    if not _meets_voting_requirements(votes, total_tokens, quorum_threshold, approval_threshold):
        return False
    
    # Apply the proposed changes to a copy of the network
    new_performances = node_performances.copy()
    new_edges = edges.copy()
    new_dependencies = [deps.copy() for deps in node_dependencies]
    
    # Apply proposal changes
    if proposal['type'] == 'boost':
        node_id = proposal['node_id']
        percentage = proposal['percentage']
        new_performances[node_id] *= (1 + percentage / 100)
    elif proposal['type'] == 'reconfigure':
        node1, node2 = proposal['node1'], proposal['node2']
        edge = (min(node1, node2), max(node1, node2))
        if proposal['add_connection']:
            if edge not in new_edges:
                new_edges.append(edge)
        else:
            if edge in new_edges:
                new_edges.remove(edge)
    elif proposal['type'] == 'dependency':
        node_id = proposal['node_id']
        new_dependencies[node_id] = proposal['new_dependencies'].copy()
    
    # Check network stability
    return _is_network_stable(N, new_edges, new_performances, new_dependencies, influence_factor, critical_threshold)

def _meets_voting_requirements(votes, total_tokens, quorum_threshold, approval_threshold):
    if not votes:
        return False
    
    total_voting_power = sum(abs(vote) for vote in votes)
    if total_voting_power < quorum_threshold * total_tokens:
        return False
    
    yes_votes = sum(vote for vote in votes if vote > 0)
    no_votes = -sum(vote for vote in votes if vote < 0)
    total_votes = yes_votes + no_votes
    
    if total_votes == 0:
        return False
    
    approval_ratio = yes_votes / total_votes
    return approval_ratio >= approval_threshold

def _is_network_stable(N, edges, performances, dependencies, influence_factor, critical_threshold):
    # Calculate adjusted performances
    adjusted_performances = performances.copy()
    
    # We need to handle potential circular dependencies by iterating until convergence
    changed = True
    max_iterations = 100
    iteration = 0
    
    while changed and iteration < max_iterations:
        changed = False
        new_adjusted = adjusted_performances.copy()
        
        for i in range(N):
            if not dependencies[i]:
                # No dependencies, performance remains unchanged
                continue
                
            # Calculate average dependency performance
            dep_performances = [adjusted_performances[dep] for dep in dependencies[i]]
            avg_dep_performance = sum(dep_performances) / len(dep_performances)
            
            # Calculate new adjusted performance
            if performances[i] == 0:
                # Handle division by zero
                new_performance = 0
            else:
                performance_diff = max(0, (avg_dep_performance - performances[i]) / performances[i])
                new_performance = performances[i] * (1 - influence_factor * performance_diff)
            
            if not math.isclose(new_performance, adjusted_performances[i], rel_tol=1e-6):
                changed = True
                new_adjusted[i] = new_performance
        
        adjusted_performances = new_adjusted
        iteration += 1
    
    # Check if all nodes meet critical threshold
    return all(perf >= critical_threshold for perf in adjusted_performances)