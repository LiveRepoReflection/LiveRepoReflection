import math

def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def validate_inputs(N: int, M: int, K: int, T: int,
                   sensor_locations: List[Tuple[float, float]],
                   sensor_ranges: List[int],
                   region_locations: List[Tuple[float, float]],
                   region_importances: List[int]) -> bool:
    if len(sensor_locations) != N or len(sensor_ranges) != N:
        return False
    if len(region_locations) != M or len(region_importances) != M:
        return False
    if any(r < 0 for r in sensor_ranges):
        return False
    if any(imp < 0 for imp in region_importances):
        return False
    return True