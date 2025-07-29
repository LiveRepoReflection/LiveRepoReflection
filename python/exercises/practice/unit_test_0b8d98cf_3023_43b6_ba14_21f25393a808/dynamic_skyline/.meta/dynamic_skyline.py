import heapq

class SkylineManager:
    def __init__(self):
        self.buildings = []

    def add_building(self, left, right, height):
        # It is guaranteed that left < right and height > 0.
        self.buildings.append((left, right, height))

    def remove_building(self, left, right, height):
        # It is guaranteed that the exact building exists.
        self.buildings.remove((left, right, height))

    def get_skyline(self):
        # If there are no buildings, return an empty skyline.
        if not self.buildings:
            return []
            
        # Create events for all buildings
        # A start event is represented as (x, -height, right)
        # An end event is represented as (x, 0, None)
        events = []
        for left, right, height in self.buildings:
            events.append((left, -height, right))
            events.append((right, 0, None))
        
        # Sort events:
        # Primary key: x-coordinate (ascending).
        # Secondary key: height value, ensuring start events (-height) come before end events (0).
        # Tertiary key: right coordinate.
        events.sort()
        
        # Max-heap with dummy building (height=0, extends to infinity)
        heap = [(0, float('inf'))]
        result = []
        prev_height = 0
        idx = 0
        n = len(events)
        while idx < n:
            # Process all events at the same x-coordinate.
            current_x = events[idx][0]
            while idx < n and events[idx][0] == current_x:
                x, neg_height, right = events[idx]
                if neg_height != 0:
                    # Start event: add building to the heap.
                    heapq.heappush(heap, (neg_height, right))
                # End events are not pushed; they simply trigger heap cleanup.
                idx += 1

            # Remove any buildings in the heap that have ended (their right coordinate <= current x).
            while heap and heap[0][1] <= current_x:
                heapq.heappop(heap)
            
            # Current height is the negative of the top of the heap.
            current_height = -heap[0][0] if heap else 0
            if current_height != prev_height:
                result.append((current_x, current_height))
                prev_height = current_height
        return result