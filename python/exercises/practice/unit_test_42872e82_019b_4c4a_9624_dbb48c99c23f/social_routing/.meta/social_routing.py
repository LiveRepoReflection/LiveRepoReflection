from collections import defaultdict, deque
from typing import Dict, Set, Optional

class SocialNetwork:
    def __init__(self):
        # Adjacency list to store friendships
        self._friends: Dict[int, Set[int]] = defaultdict(set)
        # Set to keep track of all users
        self._users: Set[int] = set()

    def addUser(self, userID: int) -> None:
        """Add a new user to the network."""
        self._users.add(userID)

    def removeUser(self, userID: int) -> None:
        """Remove a user and all their friendships from the network."""
        if userID not in self._users:
            return

        # Remove all friendships involving this user
        for friend in self._friends[userID]:
            self._friends[friend].remove(userID)
        
        # Remove the user's friendship list and the user
        del self._friends[userID]
        self._users.remove(userID)

    def addFriendship(self, userID1: int, userID2: int) -> None:
        """Add a bi-directional friendship between two users."""
        # Verify both users exist
        if userID1 not in self._users or userID2 not in self._users:
            return
        
        # Add bi-directional friendship
        self._friends[userID1].add(userID2)
        self._friends[userID2].add(userID1)

    def removeFriendship(self, userID1: int, userID2: int) -> None:
        """Remove the friendship between two users."""
        # Check if both users exist
        if userID1 not in self._users or userID2 not in self._users:
            return

        # Remove bi-directional friendship
        self._friends[userID1].discard(userID2)
        self._friends[userID2].discard(userID1)

    def getRoute(self, userID1: int, userID2: int, K: int) -> int:
        """
        Find the shortest path between two users within K hops.
        Returns the number of hops needed or -1 if no path exists within K hops.
        """
        # Check if users exist
        if userID1 not in self._users or userID2 not in self._users:
            return -1

        # Special case: same user
        if userID1 == userID2:
            return 0

        # Special case: K = 0
        if K == 0:
            return -1

        # Use modified BFS to find shortest path within K hops
        visited = {userID1}
        # Queue stores (user, distance) pairs
        queue = deque([(userID1, 0)])

        while queue:
            current_user, distance = queue.popleft()

            # If we've exceeded K hops, skip this path
            if distance >= K:
                continue

            # Check all friends of current user
            for friend in self._friends[current_user]:
                if friend == userID2:
                    # Found target user
                    return distance + 1
                
                if friend not in visited:
                    visited.add(friend)
                    queue.append((friend, distance + 1))

        # No path found within K hops
        return -1

    def _validateUserID(self, userID: int) -> bool:
        """Validate if a userID is within acceptable range."""
        return 1 <= userID <= 10**9
