def validate_airports(airports):
    if not isinstance(airports, list):
        raise ValueError("Airports must be a list")
    if len(airports) != len(set(airports)):
        raise ValueError("Airport IDs must be unique")
    if not all(isinstance(a, int) for a in airports):
        raise ValueError("All airport IDs must be integers")

def validate_routes(routes):
    if not isinstance(routes, list):
        raise ValueError("Routes must be a list")
    for route in routes:
        if len(route) != 3:
            raise ValueError("Each route must be a tuple of (src, dest, cost)")
        if not all(isinstance(x, int) for x in route[:2]):
            raise ValueError("Source and destination must be integers")
        if not isinstance(route[2], (int, float)) or route[2] <= 0:
            raise ValueError("Cost must be a positive number")