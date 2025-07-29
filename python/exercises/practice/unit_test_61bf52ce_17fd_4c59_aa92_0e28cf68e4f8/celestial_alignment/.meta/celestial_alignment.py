from typing import List, Dict, Tuple, Set
import heapq
from collections import defaultdict

def optimize_observations(
    observatories: List[str],
    objects: List[str],
    time_slots: int,
    observatory_capacities: Dict[str, int],
    visibility_scores: Dict[Tuple[str, str, int], float],
    object_dependencies: Dict[Tuple[str, int], Dict[Tuple[str, int], float]]
) -> Dict[Tuple[str, str, int], bool]:
    
    # Handle empty input cases
    if not observatories or not objects or time_slots == 0:
        return {}

    # Initialize result dictionary
    result = {}
    
    # Create a graph structure for storing scores and dependencies
    score_graph = defaultdict(list)
    
    # Build the score graph including both visibility scores and dependencies
    for (obs, obj, slot), score in visibility_scores.items():
        if score > 0:  # Only consider positive visibility scores
            score_graph[(obs, slot)].append((score, obj, None))
            
    # Add dependency edges to the graph
    for (obj1, slot1), dependencies in object_dependencies.items():
        for (obj2, slot2), dep_score in dependencies.items():
            if dep_score > 0:  # Only consider positive dependencies
                for obs in observatories:
                    if (obs, obj1, slot1) in visibility_scores and (obs, obj2, slot2) in visibility_scores:
                        score_graph[(obs, slot1)].append((dep_score, obj1, (obj2, slot2)))

    # Track used capacity for each observatory
    used_capacity = defaultdict(int)
    
    # Track allocated objects per time slot
    allocated_objects = defaultdict(set)
    
    # Priority queue to process highest scoring observations first
    pq = []
    
    # Initialize priority queue with all possible observations
    for obs in observatories:
        for slot in range(time_slots):
            for score, obj, dep in score_graph[(obs, slot)]:
                heapq.heappush(pq, (-score, obs, obj, slot, dep))
    
    # Process observations in order of decreasing score
    while pq:
        score, obs, obj, slot, dep = heapq.heappop(pq)
        score = -score  # Convert back to positive score
        
        # Check if this observation is valid
        if (used_capacity[obs] < observatory_capacities[obs] and  # Check capacity
            obj not in allocated_objects[slot] and  # Check no overlap
            (obs, obj, slot) in visibility_scores):  # Verify visibility
            
            # If there's a dependency, check if it can be satisfied
            can_add = True
            if dep:
                dep_obj, dep_slot = dep
                # Only add if the dependent object can be observed
                if dep_obj in allocated_objects[dep_slot]:
                    can_add = False
            
            if can_add:
                # Add the observation to result
                result[(obs, obj, slot)] = True
                used_capacity[obs] += 1
                allocated_objects[slot].add(obj)
                
                # If this observation has dependencies, update scores for dependent objects
                if (obj, slot) in object_dependencies:
                    for (dep_obj, dep_slot), dep_score in object_dependencies[(obj, slot)].items():
                        if dep_score > 0:
                            # Add new potential observations with updated scores
                            for dep_obs in observatories:
                                if (dep_obs, dep_obj, dep_slot) in visibility_scores:
                                    new_score = visibility_scores[(dep_obs, dep_obj, dep_slot)] + dep_score
                                    heapq.heappush(pq, (-new_score, dep_obs, dep_obj, dep_slot, None))

    return result

def calculate_total_score(
    result: Dict[Tuple[str, str, int], bool],
    visibility_scores: Dict[Tuple[str, str, int], float],
    object_dependencies: Dict[Tuple[str, int], Dict[Tuple[str, int], float]]
) -> float:
    """Helper function to calculate the total score of an allocation"""
    total_score = 0.0
    
    # Add visibility scores
    for allocation in result:
        if allocation in visibility_scores:
            total_score += visibility_scores[allocation]
    
    # Add dependency scores
    for (obj1, slot1), dependencies in object_dependencies.items():
        for (obj2, slot2), dep_score in dependencies.items():
            # Check if both objects are observed
            for obs1 in set(obs for (obs, o, s) in result if o == obj1 and s == slot1):
                for obs2 in set(obs for (obs, o, s) in result if o == obj2 and s == slot2):
                    total_score += dep_score
                    
    return total_score