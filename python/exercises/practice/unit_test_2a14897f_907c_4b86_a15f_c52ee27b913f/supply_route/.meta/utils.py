def calculate_distance(loc1, loc2):
    """Calculate Euclidean distance between two points"""
    lat1, lon1 = loc1
    lat2, lon2 = loc2
    return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)

def validate_input(warehouses, hubs, travel_times, costs, max_time):
    """Validate input dimensions and constraints"""
    num_warehouses = len(warehouses)
    num_hubs = len(hubs)
    
    if num_warehouses != len(travel_times) or num_warehouses != len(costs):
        raise ValueError("Warehouse count doesn't match travel_times or costs dimensions")
    
    for i in range(num_warehouses):
        if len(travel_times[i]) != num_hubs or len(costs[i]) != num_hubs:
            raise ValueError("Hub count doesn't match travel_times or costs dimensions")
    
    for w in warehouses:
        if 'capacity' not in w or 'location' not in w:
            raise ValueError("Warehouse missing required fields")
    
    for h in hubs:
        if 'demand' not in h or 'location' not in h:
            raise ValueError("Hub missing required fields")