import math
from itertools import combinations
from collections import defaultdict

def optimize_highways(cities, max_highway_length, budget):
    if not cities:
        return []
    
    if len(cities) == 1:
        return []
    
    city_dict = {cid: (x, y, pop) for cid, x, y, pop in cities}
    
    # Generate all possible valid highway segments
    possible_highways = []
    for (cid1, cid2) in combinations(city_dict.keys(), 2):
        x1, y1, _ = city_dict[cid1]
        x2, y2, _ = city_dict[cid2]
        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        if distance <= max_highway_length:
            pop1 = city_dict[cid1][2]
            pop2 = city_dict[cid2][2]
            benefit = pop1 * pop2
            possible_highways.append((cid1, cid2, distance, benefit))
    
    if not possible_highways:
        raise ValueError("No valid highway connections possible within given constraints")
    
    # Sort highways by benefit-to-cost ratio (descending)
    possible_highways.sort(key=lambda x: x[3]/x[2], reverse=True)
    
    selected_highways = []
    total_cost = 0
    connected_components = {cid: cid for cid in city_dict.keys()}
    
    def find_root(cid):
        while connected_components[cid] != cid:
            connected_components[cid] = connected_components[connected_components[cid]]
            cid = connected_components[cid]
        return cid
    
    for hw in possible_highways:
        cid1, cid2, cost, _ = hw
        root1 = find_root(cid1)
        root2 = find_root(cid2)
        
        if root1 != root2:
            if total_cost + cost <= budget:
                selected_highways.append((cid1, cid2))
                total_cost += cost
                connected_components[root2] = root1
    
    # Verify all cities are connected
    roots = set()
    for cid in city_dict.keys():
        roots.add(find_root(cid))
        if len(roots) > 1:
            raise ValueError("Cannot connect all cities within given budget and constraints")
    
    return selected_highways