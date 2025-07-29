import itertools
import copy

def optimize_router_config(N, adjacency_list, initial_scores, target_router, potential_changes, influence_matrix):
    # Use a tolerance for floating point comparisons
    TOL = 1e-9

    # Check if a value is within bounds [0, 1000]
    def within_bounds(value):
        return 0 - TOL <= value <= 1000 + TOL

    m = len(potential_changes)
    max_target_score = initial_scores[target_router]
    
    # helper function to simulate the application of a sequence of changes
    def simulate(sequence):
        # work with a copy of scores as floats
        scores = [float(s) for s in initial_scores]
        for idx in sequence:
            router_id, change_amount = potential_changes[idx]
            # Calculate new score for the router
            new_score = scores[router_id] + change_amount
            if not within_bounds(new_score):
                return None  # invalid sequence
            # calculate new scores for neighbors (only those in adjacency_list[router_id])
            new_neighbor_scores = {}
            for neighbor in adjacency_list[router_id]:
                # neighbor update using influence, if neighbor exists in influence_matrix row.
                # We assume influence_matrix is available for all router pairs.
                increment = influence_matrix[router_id][neighbor] * change_amount
                new_val = scores[neighbor] + increment
                if not within_bounds(new_val):
                    return None  # invalid sequence
                new_neighbor_scores[neighbor] = new_val
            # Update the router's own score
            scores[router_id] = new_score
            # Update all neighbors' scores
            for neighbor, val in new_neighbor_scores.items():
                scores[neighbor] = val
        return scores

    # Loop over all subsets of potential changes; use bitmask
    indices = list(range(m))
    # Consider empty subset (no changes) as valid simulation
    best_scores = [float(s) for s in initial_scores]
    max_target_score = best_scores[target_router]
    
    for k in range(1, m+1):
        for subset in itertools.combinations(indices, k):
            # For each permutation of this subset
            for perm in itertools.permutations(subset):
                result = simulate(perm)
                if result is not None:
                    if result[target_router] > max_target_score + TOL:
                        max_target_score = result[target_router]
    # Return maximum achievable target router score rounded as int if within tolerance
    # Check if max_target_score is nearly integer
    if abs(max_target_score - round(max_target_score)) < TOL:
        return int(round(max_target_score))
    else:
        return max_target_score