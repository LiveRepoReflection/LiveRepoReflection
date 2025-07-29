class UnionFind:
    def __init__(self):
        self.parent = {}
        self.rank = {}
        self.size = {}
        self.max_size = 0
        self.components = 0

    def make_set(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            self.size[x] = 1
            self.components += 1
            self.max_size = max(self.max_size, 1)

    def find(self, x):
        if x not in self.parent:
            return None
        
        # Path compression
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x is None or root_y is None or root_x == root_y:
            return

        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            root_x, root_y = root_y, root_x

        self.parent[root_y] = root_x
        self.size[root_x] += self.size[root_y]
        
        if self.rank[root_x] == self.rank[root_y]:
            self.rank[root_x] += 1

        # Update component count and max size
        self.components -= 1
        self.max_size = max(self.max_size, self.size[root_x])

    def remove_element(self, x):
        if x not in self.parent:
            return

        root = self.find(x)
        self.size[root] -= 1
        
        if self.size[root] == 0:
            self.components -= 1
        
        del self.parent[x]
        del self.rank[x]
        
        # Recalculate max_size
        self.max_size = max(self.size.values()) if self.size else 0


class SocialNetwork:
    def __init__(self):
        self.uf = UnionFind()
        self.connections = {}  # Adjacency list representation

    def add_user(self, user_id):
        if user_id not in self.connections:
            self.connections[user_id] = set()
            self.uf.make_set(user_id)

    def remove_user(self, user_id):
        if user_id not in self.connections:
            return

        # Remove all connections involving this user
        for neighbor in self.connections[user_id].copy():
            self.remove_connection(user_id, neighbor)

        # Remove user from the network
        del self.connections[user_id]
        self.uf.remove_element(user_id)

    def add_connection(self, user1_id, user2_id):
        if (user1_id not in self.connections or 
            user2_id not in self.connections or 
            user1_id == user2_id):
            return

        if user2_id not in self.connections[user1_id]:
            self.connections[user1_id].add(user2_id)
            self.connections[user2_id].add(user1_id)
            self.uf.union(user1_id, user2_id)

    def remove_connection(self, user1_id, user2_id):
        if (user1_id not in self.connections or 
            user2_id not in self.connections):
            return

        if user2_id in self.connections[user1_id]:
            self.connections[user1_id].remove(user2_id)
            self.connections[user2_id].remove(user1_id)
            
            # Rebuild communities after removing connection
            self._rebuild_communities()

    def get_largest_community_size(self):
        return self.uf.max_size

    def get_community_count(self):
        return self.uf.components

    def are_users_connected(self, user1_id, user2_id):
        if (user1_id not in self.connections or 
            user2_id not in self.connections):
            return False
            
        return self.uf.find(user1_id) == self.uf.find(user2_id)

    def _rebuild_communities(self):
        # Reset Union-Find data structure
        new_uf = UnionFind()
        
        # Add all users
        for user in self.connections:
            new_uf.make_set(user)
        
        # Rebuild all connections
        processed = set()
        for user in self.connections:
            processed.add(user)
            for neighbor in self.connections[user]:
                if neighbor not in processed:
                    new_uf.union(user, neighbor)
        
        self.uf = new_uf