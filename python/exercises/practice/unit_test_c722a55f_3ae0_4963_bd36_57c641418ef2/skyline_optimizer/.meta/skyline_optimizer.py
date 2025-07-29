import heapq

def get_skyline(buildings):
    # Return empty skyline if no buildings are provided.
    if not buildings:
        return []
    
    # Create events: For each building, add a start event and an end event.
    events = []
    for L, R, H in buildings:
        # Start event: height is negative to simulate a max-heap.
        events.append((L, -H, R))
        # End event: height 0 signifies a removal event.
        events.append((R, 0, None))
    
    # Sort events by x-coordinate.
    # For the same x-coordinate, start events (-H) come before end events (0),
    # ensuring a building's height is considered before removal.
    events.sort(key=lambda x: (x[0], x[1]))

    # Initialize the result list and a heap.
    # Heap stores tuples of (negative height, end coordinate).
    # Starting with a dummy ground level building.
    result = []
    heap = [(0, float('inf'))]
    prev_height = 0

    for x, h, R in events:
        if h < 0:
            # Start event: push the building into the heap.
            heapq.heappush(heap, (h, R))
        else:
            # End event: remove buildings that have ended.
            # Lazy removal: Pop from the heap while the current building has ended.
            while heap and heap[0][1] <= x:
                heapq.heappop(heap)
        # Current maximum height.
        current_height = -heap[0][0]
        # If the current maximum height has changed, add a key point.
        if current_height != prev_height:
            # Avoid redundant consecutive key points at the same x-coordinate.
            if result and result[-1][0] == x:
                result[-1] = (x, current_height)
            else:
                result.append((x, current_height))
            prev_height = current_height

    return result