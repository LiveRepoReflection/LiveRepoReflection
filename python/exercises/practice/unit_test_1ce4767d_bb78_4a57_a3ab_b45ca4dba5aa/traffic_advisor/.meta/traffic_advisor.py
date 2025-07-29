import sys

def main():
    # Read all input lines
    input_lines = sys.stdin.read().strip().splitlines()
    if not input_lines:
        return

    # Parse header: N (rows), M (columns) and K (number of intersections)
    header = input_lines[0].split()
    if len(header) < 3:
        return
    N, M, K = map(int, header)
    
    # Read grid lines and intersections (ignore grid and intersections details for this basic solution)
    grid_start = 1
    grid_end = grid_start + N
    grid_lines = input_lines[grid_start:grid_end]
    
    intersections_start = grid_end
    intersections_end = intersections_start + K
    intersections = input_lines[intersections_start:intersections_end]
    
    # Read the vehicle count (last line)
    if intersections_end < len(input_lines):
        vehicles_count = int(input_lines[intersections_end])
    else:
        vehicles_count = 0

    # For a baseline solution, we output a fixed configuration for the traffic lights.
    # According to the problem constraints, each light configuration (G, R) must be within 0 <= value <= 20.
    # Here, we simply choose a default configuration of (10, 10) for each intersection.
    for _ in range(K):
        print("10 10")

if __name__ == '__main__':
    main()