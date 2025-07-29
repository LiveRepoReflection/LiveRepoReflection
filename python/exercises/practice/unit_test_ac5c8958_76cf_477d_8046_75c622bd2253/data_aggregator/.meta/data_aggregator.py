from typing import Dict, List, Union
from collections import defaultdict
import threading
from statistics import mean

class DataAggregator:
    def __init__(self, tree: Dict[str, Dict]):
        """Initialize the data aggregator with a tree structure."""
        self.tree = tree
        self._cache = {}  # Cache for storing computed aggregates
        self._cache_lock = threading.Lock()
        self._validate_tree()
        self._build_parent_map()

    def _validate_tree(self) -> None:
        """Validate the tree structure."""
        # Verify that each node has required keys
        for node_id, node_data in self.tree.items():
            if not isinstance(node_data, dict):
                raise ValueError(f"Node {node_id} data must be a dictionary")
            if 'children' not in node_data or 'data' not in node_data:
                raise ValueError(f"Node {node_id} missing required keys")
            if not isinstance(node_data['children'], list):
                raise ValueError(f"Node {node_id} children must be a list")
            if not isinstance(node_data['data'], list):
                raise ValueError(f"Node {node_id} data must be a list")

    def _build_parent_map(self) -> None:
        """Build a mapping of child nodes to their parents."""
        self.parent_map = {}
        for node_id, node_data in self.tree.items():
            for child in node_data['children']:
                self.parent_map[child] = node_id

    def _get_subtree_data(self, node_id: str) -> List[float]:
        """Recursively collect all data points in a subtree."""
        if node_id not in self.tree:
            raise KeyError(f"Node {node_id} not found in tree")

        # Check cache first
        with self._cache_lock:
            if node_id in self._cache:
                return self._cache[node_id]

        node = self.tree[node_id]
        data = node['data'].copy()  # Start with node's own data

        # Recursively collect data from children
        for child in node['children']:
            data.extend(self._get_subtree_data(child))

        # Cache the result
        with self._cache_lock:
            self._cache[node_id] = data

        return data

    def _invalidate_cache(self, node_id: str) -> None:
        """Invalidate cache entries for a node and its ancestors."""
        with self._cache_lock:
            current = node_id
            while current is not None:
                if current in self._cache:
                    del self._cache[current]
                current = self.parent_map.get(current)

    def update_data(self, node_id: str, new_data: List[float]) -> None:
        """Update data for a specific node."""
        if node_id not in self.tree:
            raise KeyError(f"Node {node_id} not found in tree")

        self.tree[node_id]['data'] = new_data
        self._invalidate_cache(node_id)

    def query(self, node_id: str, statistic: str) -> float:
        """
        Query for an aggregate statistic on a subtree.
        
        Args:
            node_id: The root of the subtree to query
            statistic: One of 'min', 'max', 'sum', 'average'
        
        Returns:
            The computed statistic
        """
        data = self._get_subtree_data(node_id)
        
        if not data:
            raise ValueError(f"No data available for node {node_id}")

        if statistic == 'min':
            return min(data)
        elif statistic == 'max':
            return max(data)
        elif statistic == 'sum':
            return sum(data)
        elif statistic == 'average':
            return mean(data)
        else:
            raise ValueError(f"Invalid statistic: {statistic}")

    def add_data_point(self, node_id: str, value: float) -> None:
        """Add a single data point to a node."""
        if node_id not in self.tree:
            raise KeyError(f"Node {node_id} not found in tree")

        self.tree[node_id]['data'].append(value)
        self._invalidate_cache(node_id)

    def remove_node(self, node_id: str) -> None:
        """Remove a node from the tree (simulating device failure)."""
        if node_id not in self.tree:
            raise KeyError(f"Node {node_id} not found in tree")

        # Remove node from parent's children list
        if node_id in self.parent_map:
            parent_id = self.parent_map[node_id]
            self.tree[parent_id]['children'].remove(node_id)
            self._invalidate_cache(parent_id)

        # Remove node and all its descendants
        nodes_to_remove = [node_id]
        stack = [node_id]
        
        while stack:
            current = stack.pop()
            stack.extend(self.tree[current]['children'])
            nodes_to_remove.append(current)

        for node in nodes_to_remove:
            if node in self.tree:
                del self.tree[node]
                if node in self.parent_map:
                    del self.parent_map[node]