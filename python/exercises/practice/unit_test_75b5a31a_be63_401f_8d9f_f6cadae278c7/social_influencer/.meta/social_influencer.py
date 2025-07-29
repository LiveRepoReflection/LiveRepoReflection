import threading
from collections import deque

class SocialNetwork:
    def __init__(self):
        self.users = {}  # {user_id: {"name": name, "attributes": {}}}
        self.friends = {}  # {user_id: set(friend_ids)}
        self.lock = threading.RLock()

    def add_user(self, user_id: int, name: str, attributes: dict) -> bool:
        with self.lock:
            if user_id in self.users:
                return False
            self.users[user_id] = {"name": name, "attributes": attributes.copy()}
            self.friends[user_id] = set()
            return True

    def add_friendship(self, user_id1: int, user_id2: int) -> bool:
        with self.lock:
            if user_id1 not in self.users or user_id2 not in self.users:
                return False
            if user_id2 in self.friends[user_id1]:
                return False
            self.friends[user_id1].add(user_id2)
            self.friends[user_id2].add(user_id1)
            return True

    def get_friends(self, user_id: int) -> set:
        with self.lock:
            if user_id not in self.users:
                return set()
            return set(self.friends[user_id])

    def get_user_attributes(self, user_id: int) -> dict:
        with self.lock:
            if user_id not in self.users:
                return {}
            return self.users[user_id]["attributes"].copy()

    def get_influencers(self, user_id: int, degree: int, attribute_key: str) -> list:
        with self.lock:
            if user_id not in self.users:
                return []
            # Handle negative degree as 0 (only the user itself)
            max_degree = degree if degree >= 0 else 0

            # BFS traversal up to max_degree levels
            visited = set()
            influencers = {}
            queue = deque()
            queue.append((user_id, 0))
            visited.add(user_id)

            while queue:
                current, dist = queue.popleft()
                # Process influencer score for the current node
                score = 0
                attr = self.users[current].get("attributes", {})
                value = attr.get(attribute_key, "0")
                try:
                    score = int(value)
                except (ValueError, TypeError):
                    score = 0
                influencers[current] = score

                # If within allowable degree, add friends to the queue
                if dist < max_degree:
                    for friend in self.friends.get(current, set()):
                        if friend not in visited:
                            visited.add(friend)
                            queue.append((friend, dist + 1))

            # Prepare result list: each tuple is (user_id, score)
            # Ensure starting user is present, it will be as part of BFS
            result = [(uid, influencers[uid]) for uid in influencers]
            # Sort: primary by descending reach, secondary by ascending user_id
            result.sort(key=lambda x: (-x[1], x[0]))
            return result