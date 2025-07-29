from collections import defaultdict
from typing import List, Tuple, Set
import heapq

def find_most_resilient_component(num_labs: int, entanglement_links: List[Tuple[int, int, int]]) -> int:
    """
    Find the resilience score of the most resilient connected component in the quantum network.
    
    Args:
        num_labs: Number of labs in the network (numbered from 0 to num_labs-1)
        entanglement_links: List of tuples (lab1, lab2, fragility) representing quantum entanglement links
        
    Returns:
        The resilience score of the most resilient connected component
    
    Raises:
        ValueError: If input parameters are invalid
    """
    # Input validation
    if num_labs < 0:
        raise ValueError("Number of labs cannot be negative")
    if num_labs > 10**5:
        raise ValueError("Number of labs exceeds maximum limit")
    if len(entanglement_links) > 2 * 10**5:
        raise ValueError("Number of links exceeds maximum limit")

    if num_labs == 0 or not entanglement_links:
        return 0

    # Create adjacency list representation of the network
    graph = defaultdict(list)
    
    # Process and validate links
    for lab1, lab2, fragility in entanglement_links:
        # Validate lab indices
        if not (0 <= lab1 < num_labs and 0 <= lab2 < num_labs):
            raise ValueError("Invalid lab index")
        # Validate fragility score
        if not (0 <= fragility <= 10**9):
            raise ValueError("Invalid fragility score")
        
        # Skip self-loops
        if lab1 == lab2:
            continue
            
        # Add edges (undirected graph)
        graph[lab1].append((lab2, fragility))
        graph[lab2].append((lab1, fragility))

    def find_component_resilience(start: int, visited: Set[int]) -> int:
        """
        Find the minimum fragility score in a connected component using DFS.
        
        Args:
            start: Starting lab index
            visited: Set of visited labs
            
        Returns:
            Minimum fragility score in the component
        """
        if start in visited:
            return float('inf')
            
        component_min_fragility = float('inf')
        stack = [(start, float('inf'))]
        component_visited = set()
        
        while stack:
            current_lab, current_min = stack.pop()
            if current_lab in component_visited:
                continue
                
            component_visited.add(current_lab)
            visited.add(current_lab)
            component_min_fragility = min(component_min_fragility, current_min)
            
            for next_lab, fragility in graph[current_lab]:
                if next_lab not in component_visited:
                    stack.append((next_lab, fragility))
                    
        return component_min_fragility if component_min_fragility != float('inf') else 0

    # Find all connected components and their resilience scores
    visited = set()
    max_resilience = 0
    
    for lab in range(num_labs):
        if lab not in visited:
            resilience = find_component_resilience(lab, visited)
            max_resilience = max(max_resilience, resilience)
    
    return max_resilience