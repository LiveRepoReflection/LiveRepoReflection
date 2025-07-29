import threading
from collections import defaultdict, deque
import heapq


class HyperSocialNetwork:
    def __init__(self):
        """
        Initialize the HyperSocialNetwork with necessary data structures
        """
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        self._users = set()  # Set of user IDs
        self._groups = {}  # Map from group ID to set of user IDs
        self._latest_timestamp = 0  # Track the latest interaction timestamp
        
        # Adjacency lists for group interactions: {source_group: [(target_group, timestamp), ...]}
        self._outgoing_interactions = defaultdict(list)
        
        # Inverse adjacency list for quick lookup of incoming interactions
        self._incoming_interactions = defaultdict(list)

    def create_user(self, user_id):
        """
        Create a new user with the given user_id.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            True if successful, False if the user ID already exists
        """
        with self._lock:
            if user_id in self._users:
                return False
            
            self._users.add(user_id)
            return True

    def create_group(self, group_id, user_ids):
        """
        Create a new group with the given group_id containing the set of user_ids.
        
        Args:
            group_id: Unique identifier for the group
            user_ids: List of user IDs to include in the group
            
        Returns:
            True if successful, False if the group ID already exists or if any user ID does not exist
        """
        with self._lock:
            if group_id in self._groups:
                return False
            
            # Verify all users exist
            user_ids_set = set(user_ids)
            if not user_ids_set.issubset(self._users):
                return False
            
            self._groups[group_id] = user_ids_set
            return True

    def record_interaction(self, group_ids, timestamp):
        """
        Record a new interaction between the groups specified by group_ids at the given timestamp.
        
        Args:
            group_ids: List of group IDs defining the direction of the interaction
            timestamp: Time of the interaction
            
        Returns:
            True if successful, False if any group ID does not exist or timestamp is invalid
        """
        with self._lock:
            # Check if timestamp is valid (strictly increasing)
            if timestamp <= self._latest_timestamp:
                return False
            
            # Check if all groups exist
            if not group_ids or not all(group_id in self._groups for group_id in group_ids):
                return False
            
            # Record the interactions between consecutive groups
            for i in range(len(group_ids) - 1):
                source_group = group_ids[i]
                target_group = group_ids[i + 1]
                
                # Record outgoing interaction
                self._outgoing_interactions[source_group].append((target_group, timestamp))
                
                # Record incoming interaction for easier lookup
                self._incoming_interactions[target_group].append((source_group, timestamp))
            
            # Update the latest timestamp
            self._latest_timestamp = timestamp
            
            return True

    def get_interacting_groups(self, group_id, start_time, end_time):
        """
        Get a list of group IDs that have interacted with the given group_id within the time range.
        
        Args:
            group_id: Target group ID
            start_time: Start of time range (inclusive)
            end_time: End of time range (exclusive)
            
        Returns:
            List of group IDs sorted in ascending order
        """
        with self._lock:
            if group_id not in self._groups:
                return []
                
            # Find all groups that have interacted with the target group in the time range
            interacting_groups = set()
            
            for source_group, timestamp in self._incoming_interactions[group_id]:
                if start_time <= timestamp < end_time:
                    interacting_groups.add(source_group)
            
            # Return the list of group IDs sorted in ascending order
            return sorted(list(interacting_groups))

    def get_interaction_path(self, start_group_id, end_group_id, max_length, start_time, end_time):
        """
        Find a path of interactions from start_group_id to end_group_id within the specified constraints.
        
        Args:
            start_group_id: Source group ID
            end_group_id: Target group ID
            max_length: Maximum number of interactions in the path
            start_time: Start of time range (inclusive)
            end_time: End of time range (exclusive)
            
        Returns:
            List of group IDs representing the interaction path, or empty list if no path exists
        """
        with self._lock:
            if max_length <= 0:
                raise ValueError("max_length must be positive")
                
            if start_group_id not in self._groups or end_group_id not in self._groups:
                return []
            
            if start_time >= end_time:
                return []
            
            # Use Dijkstra's algorithm to find the shortest path
            # We're prioritizing shortest path (fewest interactions)
            visited = set()
            # Priority queue: (path_length, current_group, path)
            pq = [(0, start_group_id, [start_group_id])]
            
            while pq:
                path_length, current_group, path = heapq.heappop(pq)
                
                if current_group == end_group_id:
                    return path
                
                if path_length >= max_length or current_group in visited:
                    continue
                
                visited.add(current_group)
                
                # Try all outgoing interactions from the current group
                for next_group, timestamp in self._outgoing_interactions[current_group]:
                    if start_time <= timestamp < end_time and next_group not in visited:
                        new_path = path + [next_group]
                        heapq.heappush(pq, (path_length + 1, next_group, new_path))
            
            # If no path is found
            return []