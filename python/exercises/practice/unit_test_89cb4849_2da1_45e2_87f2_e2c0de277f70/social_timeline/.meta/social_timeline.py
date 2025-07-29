import threading

class DecentralizedSocialNetwork:
    def __init__(self, nodes, follower_graph):
        self.num_nodes = nodes
        self.follower_graph = follower_graph
        # Global log of posts: each post is a tuple (post_id, user_id, timestamp, content)
        self.global_posts = []
        # Simulate each node with its local log of posts.
        self.nodes = {node_id: [] for node_id in range(1, nodes + 1)}
        # Node status: True means online, False means offline.
        self.node_status = {node_id: True for node_id in range(1, nodes + 1)}
        # Lock for synchronizing post creations and node operations.
        self.lock = threading.Lock()

    def create_post(self, post):
        """
        Create a post represented as a tuple (post_id, user_id, timestamp, content).
        The post is appended to the global log and propagated to all online nodes.
        """
        with self.lock:
            # Append to global log
            self.global_posts.append(post)
            # Propagate to online nodes
            for node_id in self.nodes:
                if self.node_status[node_id]:
                    self.nodes[node_id].append(post)

    def get_timeline(self, user_id, start_time, end_time):
        """
        Retrieves all posts in the given time range [start_time, end_time] from the users
        that the provided user follows. Timeline is ordered by timestamp in descending order.
        The query source is the global log ensuring eventual consistency.
        """
        # Get the set of users the requestor follows.
        followed_users = self.follower_graph.get(user_id, set())
        # Filter posts from global log; include only posts whose user_id is in followed_users.
        filtered_posts = []
        with self.lock:
            for post in self.global_posts:
                pid, uid, timestamp, content = post
                if uid in followed_users and start_time <= timestamp <= end_time:
                    filtered_posts.append(post)
        # Sort posts by timestamp descending order.
        filtered_posts.sort(key=lambda post: post[2], reverse=True)
        return filtered_posts

    def simulate_node_failure(self, nodes):
        """
        Simulate node failure by marking the nodes as offline.
        """
        with self.lock:
            for node_id in nodes:
                if node_id in self.node_status:
                    self.node_status[node_id] = False
        # In a real system, failed nodes would stop processing writes.
        # Here, we simulate by not updating their local store in create_post.
        # Their local data remains as it was at failure time.

    def simulate_node_recovery(self, nodes):
        """
        Simulate node recovery. Recovered nodes get all missing posts from the global log.
        """
        with self.lock:
            for node_id in nodes:
                if node_id in self.node_status:
                    self.node_status[node_id] = True
                    # Reconcile node's local store with global posts.
                    local_posts = self.nodes[node_id]
                    local_post_ids = {post[0] for post in local_posts}
                    for post in self.global_posts:
                        if post[0] not in local_post_ids:
                            self.nodes[node_id].append(post)