import math
from itertools import combinations
from collections import defaultdict

def calculate_distance(loc1, loc2):
    return math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)

def optimize_network(DCs, customers, trucks, SLA, max_trucks_per_DC):
    # Validate inputs
    if not DCs or not customers or not trucks:
        return {"total_cost": -1, "routes": []}
    
    # Precompute distances and validate SLA constraints
    customer_dc_mapping = defaultdict(list)
    for customer in customers:
        valid_DCs = []
        for dc in DCs:
            distance = calculate_distance(customer["location"], dc["location"])
            delivery_time = distance / 60  # Assuming 60 km/h speed
            if delivery_time <= SLA and dc["capacity"] >= customer["demand"]:
                valid_DCs.append(dc)
        if not valid_DCs:
            return {"total_cost": -1, "routes": []}
        customer_dc_mapping[customer["id"]] = valid_DCs
    
    # Check total capacity
    total_demand = sum(c["demand"] for c in customers)
    total_capacity = sum(dc["capacity"] for dc in DCs)
    if total_demand > total_capacity:
        return {"total_cost": -1, "routes": []}
    
    # Greedy assignment approach (simplified for example)
    # In practice, this would use more sophisticated optimization
    assigned_routes = []
    total_cost = 0
    open_DCs = set()
    
    # Sort customers by demand descending
    sorted_customers = sorted(customers, key=lambda x: -x["demand"])
    
    for customer in sorted_customers:
        # Find best DC for this customer
        best_dc = None
        min_cost = float('inf')
        best_truck = None
        
        for dc in customer_dc_mapping[customer["id"]]:
            if dc["capacity"] < customer["demand"]:
                continue
                
            # Find best truck
            for truck in trucks:
                if truck["capacity"] >= customer["demand"]:
                    distance = calculate_distance(customer["location"], dc["location"])
                    transport_cost = distance * truck["cost_per_km"]
                    total_route_cost = transport_cost
                    
                    # Add DC fixed cost if not already open
                    if dc["id"] not in open_DCs:
                        total_route_cost += dc["fixed_cost"]
                    
                    if total_route_cost < min_cost:
                        min_cost = total_route_cost
                        best_dc = dc
                        best_truck = truck
        
        if not best_dc:
            return {"total_cost": -1, "routes": []}
        
        # Update DC capacity and mark as open
        best_dc["capacity"] -= customer["demand"]
        open_DCs.add(best_dc["id"])
        total_cost += min_cost
        
        # Create route
        assigned_routes.append({
            "DC_id": best_dc["id"],
            "truck_id": best_truck["id"],
            "customers": [customer["id"]]
        })
    
    return {
        "total_cost": int(total_cost),
        "routes": assigned_routes
    }