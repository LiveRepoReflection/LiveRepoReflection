import heapq
import math
from collections import defaultdict, deque

class SocialNetworkAnalyzer:
    def __init__(self):
        # Set of all users.
        self.users = set()
        # Directed graph: following: user -> set of users that this user follows.
        self.following = defaultdict(set)
        # Reverse directed graph: followers: user -> set of users that follow this user.
        self.followers = defaultdict(set)

    def add_user(self, user):
        if user in self.users:
            return
        self.users.add(user)
        # Initialize empty sets in dictionaries.
        self.following[user] = set()
        self.followers[user] = set()

    def remove_user(self, user):
        if user not in self.users:
            raise KeyError(f"User {user} does not exist")
        # Remove all connections involving the user.
        # Remove user from followers of those this user follows.
        for other in self.following[user]:
            self.followers[other].discard(user)
        # Remove user from following lists of their followers.
        for other in self.followers[user]:
            self.following[other].discard(user)
        # Remove user from data structures.
        del self.following[user]
        del self.followers[user]
        self.users.remove(user)

    def add_connection(self, follower, followee):
        if follower not in self.users or followee not in self.users:
            raise KeyError("One or both users do not exist")
        # Add the connection: follower follows followee.
        self.following[follower].add(followee)
        self.followers[followee].add(follower)

    def remove_connection(self, follower, followee):
        if follower not in self.users or followee not in self.users:
            raise KeyError("One or both users do not exist")
        if followee not in self.following[follower]:
            raise KeyError("Connection does not exist")
        self.following[follower].remove(followee)
        self.followers[followee].remove(follower)

    def calculate_influence_scores(self, threshold=1e-5, max_iterations=1000):
        # Use a damping factor to ensure convergence in case of cycles.
        damping = 0.5
        # Initialize influence scores: all start with 1.
        scores = {user: 1.0 for user in self.users}
        for iteration in range(max_iterations):
            new_scores = {}
            max_change = 0.0
            for user in self.users:
                # Influence = 1 + damping * sum(influence_score(follower) for follower in followers)
                total = 0.0
                for follower in self.followers[user]:
                    total += scores[follower]
                new_score = 1.0 + damping * total
                new_scores[user] = new_score
                max_change = max(max_change, abs(new_score - scores[user]))
            scores = new_scores
            if max_change < threshold:
                break
        return scores

    def detect_communities(self):
        # Convert directed graph to undirected graph for community detection.
        undirected = defaultdict(set)
        for user in self.users:
            # Neighbors are all the users followed or following the user.
            neighbors = self.following[user] | self.followers[user]
            undirected[user] = neighbors.copy()
        # Calculate total number of undirected edges (each edge counted once).
        edge_set = set()
        for u in self.users:
            for v in undirected[u]:
                if (v, u) not in edge_set:
                    edge_set.add((u, v))
        m = len(edge_set)
        if m == 0:
            # No edges, assign each user its own community.
            return {user: idx for idx, user in enumerate(self.users)}
        # Initialize each user in its own community.
        community = {user: user for user in self.users}
        # Compute degree for each user.
        degree = {user: len(undirected[user]) for user in self.users}
        # For each community, total degree sum.
        comm_degree = {user: degree[user] for user in self.users}

        improvement = True
        while improvement:
            improvement = False
            for user in self.users:
                current_comm = community[user]
                best_comm = current_comm
                best_gain = 0.0
                # Compute the sum of weights from user to each community.
                neigh_comm = defaultdict(int)
                for neighbor in undirected[user]:
                    nbr_comm = community[neighbor]
                    neigh_comm[nbr_comm] += 1  # all weights are 1
                # Remove user temporarily from its current community.
                comm_degree[current_comm] -= degree[user]
                # Evaluate gain for moving to each neighbor community.
                for comm, k_i_in in neigh_comm.items():
                    gain = (k_i_in - (comm_degree.get(comm,0) * degree[user] / (2 * m))) / m
                    if gain > best_gain:
                        best_gain = gain
                        best_comm = comm
                # Move user to best community if it improves modularity.
                if best_comm != current_comm:
                    community[user] = best_comm
                    improvement = True
                # Add user back to community degree.
                comm_degree[community[user]] = comm_degree.get(community[user], 0) + degree[user]
        return community

    def find_shortest_path(self, source, target):
        if source not in self.users or target not in self.users:
            raise KeyError("Source or target user does not exist")
        # Use A* algorithm; edges have cost 1.
        # Heuristic: difference in influence scores from target and current user.
        influence = self.calculate_influence_scores(threshold=1e-4)
        def heuristic(u):
            return abs(influence.get(target,0) - influence.get(u,0))
        # Priority queue: (f_score, g_score, current, path)
        open_set = []
        heapq.heappush(open_set, (heuristic(source), 0, source, [source]))
        closed_set = set()
        while open_set:
            f, g, current, path = heapq.heappop(open_set)
            if current == target:
                return path
            if current in closed_set:
                continue
            closed_set.add(current)
            # Neighbors from the directed graph: follow the connection from current.
            for neighbor in self.following[current]:
                if neighbor in closed_set:
                    continue
                new_g = g + 1
                new_f = new_g + heuristic(neighbor)
                heapq.heappush(open_set, (new_f, new_g, neighbor, path + [neighbor]))
        return None