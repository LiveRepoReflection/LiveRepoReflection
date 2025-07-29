import threading
from collections import defaultdict, deque
import itertools

class SocialGraph:
    def __init__(self):
        self.lock = threading.Lock()
        self.users = set()
        self.connections = defaultdict(set)
        self._betweenness_cache = None
        self._scc_cache = None

    def add_user(self, user_id):
        with self.lock:
            self.users.add(user_id)
            self._invalidate_caches()

    def remove_user(self, user_id):
        with self.lock:
            if user_id in self.users:
                self.users.remove(user_id)
                # Remove all connections involving this user
                friends = self.connections[user_id].copy()
                for friend in friends:
                    self.connections[friend].remove(user_id)
                del self.connections[user_id]
                self._invalidate_caches()

    def add_connection(self, user1, user2):
        with self.lock:
            if user1 in self.users and user2 in self.users:
                self.connections[user1].add(user2)
                self.connections[user2].add(user1)
                self._invalidate_caches()

    def remove_connection(self, user1, user2):
        with self.lock:
            if user1 in self.connections and user2 in self.connections[user1]:
                self.connections[user1].remove(user2)
                self.connections[user2].remove(user1)
                self._invalidate_caches()

    def get_users(self):
        with self.lock:
            return list(self.users)

    def get_friends(self, user_id):
        with self.lock:
            return list(self.connections.get(user_id, set()))

    def degree_of_separation(self, user1, user2):
        if user1 == user2:
            return 0
        if user1 not in self.users or user2 not in self.users:
            return -1

        visited = set()
        queue = deque([(user1, 0)])
        visited.add(user1)

        while queue:
            current, distance = queue.popleft()
            for neighbor in self.connections.get(current, set()):
                if neighbor == user2:
                    return distance + 1
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1))
        return -1

    def get_strongly_connected_components(self):
        if self._scc_cache is not None:
            return self._scc_cache

        visited = set()
        order = []
        reverse_graph = defaultdict(set)

        # Build reverse graph
        for u in self.connections:
            for v in self.connections[u]:
                reverse_graph[v].add(u)

        # First pass to get finishing times
        def dfs(node):
            stack = [(node, False)]
            while stack:
                current, processed = stack.pop()
                if processed:
                    order.append(current)
                    continue
                if current in visited:
                    continue
                visited.add(current)
                stack.append((current, True))
                for neighbor in self.connections.get(current, set()):
                    if neighbor not in visited:
                        stack.append((neighbor, False))

        for user in self.users:
            if user not in visited:
                dfs(user)

        # Second pass on reverse graph
        visited = set()
        sccs = []
        order.reverse()

        def reverse_dfs(node, component):
            stack = [node]
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                component.append(current)
                for neighbor in reverse_graph.get(current, set()):
                    if neighbor not in visited:
                        stack.append(neighbor)

        for user in order:
            if user not in visited:
                component = []
                reverse_dfs(user, component)
                sccs.append(component)

        self._scc_cache = sccs
        return sccs

    def calculate_betweenness_centrality(self, node=None):
        if self._betweenness_cache is not None and node is None:
            return self._betweenness_cache

        betweenness = defaultdict(float)
        nodes = self.users

        for s in nodes:
            # Single-source shortest paths
            P = defaultdict(list)
            sigma = defaultdict(float)
            sigma[s] = 1
            D = {}
            D[s] = 0
            Q = deque([s])
            while Q:
                v = Q.popleft()
                for w in self.connections.get(v, set()):
                    if w not in D:
                        Q.append(w)
                        D[w] = D[v] + 1
                    if D[w] == D[v] + 1:
                        sigma[w] += sigma[v]
                        P[w].append(v)

            # Accumulation
            delta = defaultdict(float)
            S = sorted(D.keys(), key=lambda x: -D[x])
            for w in S:
                for v in P[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
                if w != s:
                    betweenness[w] += delta[w]

        # Normalization
        if len(nodes) > 2:
            scale = 1 / ((len(nodes) - 1) * (len(nodes) - 2))
            for v in betweenness:
                betweenness[v] *= scale

        self._betweenness_cache = betweenness
        return betweenness if node is None else betweenness.get(node, 0)

    def create_network_partition(self, user_ids):
        partition = SocialGraph()
        with self.lock:
            for user in user_ids:
                if user in self.users:
                    partition.add_user(user)
                    for friend in self.connections.get(user, set()):
                        if friend in user_ids:
                            partition.add_connection(user, friend)
        return partition

    def _invalidate_caches(self):
        self._betweenness_cache = None
        self._scc_cache = None