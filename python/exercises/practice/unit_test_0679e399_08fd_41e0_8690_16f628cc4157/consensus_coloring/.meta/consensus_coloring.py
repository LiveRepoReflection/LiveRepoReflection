class ConsensusColoring:
    def __init__(self):
        self.nodes = {}  # Each key is a node_id and the value is a set of neighbor node_ids.
        self.colors = {}  # Each key is a node_id and the value is its assigned color.

    def add_node(self, node_id):
        if node_id not in self.nodes:
            self.nodes[node_id] = set()
            self.colors[node_id] = None

    def remove_node(self, node_id):
        if node_id not in self.nodes:
            raise Exception("Node not found")
        # Remove this node from all of its neighbors.
        for neighbor in self.nodes[node_id]:
            self.nodes[neighbor].discard(node_id)
        del self.nodes[node_id]
        del self.colors[node_id]

    def add_edge(self, node_id1, node_id2):
        if node_id1 not in self.nodes:
            raise Exception("Node {} does not exist".format(node_id1))
        if node_id2 not in self.nodes:
            raise Exception("Node {} does not exist".format(node_id2))
        self.nodes[node_id1].add(node_id2)
        self.nodes[node_id2].add(node_id1)

    def remove_edge(self, node_id1, node_id2):
        if node_id1 in self.nodes:
            self.nodes[node_id1].discard(node_id2)
        if node_id2 in self.nodes:
            self.nodes[node_id2].discard(node_id1)

    def get_color(self, node_id):
        if node_id not in self.nodes:
            raise Exception("Node not found")
        return self.colors[node_id]

    def get_neighbors(self, node_id):
        if node_id not in self.nodes:
            raise Exception("Node not found")
        return list(self.nodes[node_id])

    def converge(self):
        # Iteratively update node colors until no changes occur.
        changed = True
        while changed:
            changed = False
            # Process nodes in a sorted order for determinism.
            for node in sorted(self.nodes.keys()):
                # Gather colors of all neighbors
                neighbor_colors = set()
                for neighbor in self.nodes[node]:
                    if self.colors[neighbor] is not None:
                        neighbor_colors.add(self.colors[neighbor])
                # Find the smallest positive integer color not used by neighbors.
                new_color = 1
                while new_color in neighbor_colors:
                    new_color += 1
                if self.colors[node] != new_color:
                    self.colors[node] = new_color
                    changed = True