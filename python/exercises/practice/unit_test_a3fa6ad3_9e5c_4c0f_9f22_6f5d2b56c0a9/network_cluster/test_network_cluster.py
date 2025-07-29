import unittest
from network_cluster import NetworkClustering


class TestNetworkClustering(unittest.TestCase):
    def test_initial_state(self):
        """Test that the initial state has no clusters."""
        clustering = NetworkClustering(0.5)
        self.assertEqual(clustering.get_clusters(), [])

    def test_add_single_user(self):
        """Test adding a single user."""
        clustering = NetworkClustering(0.5)
        clusters = clustering.process_event(("add_user", 1))
        self.assertEqual(clusters, [{1}])

    def test_add_multiple_users(self):
        """Test adding multiple users without relationships."""
        clustering = NetworkClustering(0.5)
        clustering.process_event(("add_user", 1))
        clustering.process_event(("add_user", 2))
        clusters = clustering.process_event(("add_user", 3))
        self.assertEqual(sorted([sorted(list(c)) for c in clusters]), [[1], [2], [3]])

    def test_add_relationship(self):
        """Test adding a relationship between two users."""
        clustering = NetworkClustering(0.5)
        clustering.process_event(("add_user", 1))
        clustering.process_event(("add_user", 2))
        clusters = clustering.process_event(("add_relationship", 1, 2))
        self.assertEqual(clusters, [{1, 2}])

    def test_remove_relationship(self):
        """Test removing a relationship."""
        clustering = NetworkClustering(0.5)
        clustering.process_event(("add_user", 1))
        clustering.process_event(("add_user", 2))
        clustering.process_event(("add_relationship", 1, 2))
        clusters = clustering.process_event(("remove_relationship", 1, 2))
        self.assertEqual(sorted([sorted(list(c)) for c in clusters]), [[1], [2]])

    def test_remove_user(self):
        """Test removing a user."""
        clustering = NetworkClustering(0.5)
        clustering.process_event(("add_user", 1))
        clustering.process_event(("add_user", 2))
        clustering.process_event(("add_relationship", 1, 2))
        clusters = clustering.process_event(("remove_user", 2))
        self.assertEqual(clusters, [{1}])

    def test_add_relationship_nonexistent_user(self):
        """Test adding a relationship with a non-existent user."""
        clustering = NetworkClustering(0.5)
        clustering.process_event(("add_user", 1))
        clusters = clustering.process_event(("add_relationship", 1, 2))
        self.assertEqual(clusters, [{1}])

    def test_remove_relationship_nonexistent_user(self):
        """Test removing a relationship with a non-existent user."""
        clustering = NetworkClustering(0.5)
        clustering.process_event(("add_user", 1))
        clusters = clustering.process_event(("remove_relationship", 1, 2))
        self.assertEqual(clusters, [{1}])

    def test_remove_nonexistent_user(self):
        """Test removing a non-existent user."""
        clustering = NetworkClustering(0.5)
        clustering.process_event(("add_user", 1))
        clusters = clustering.process_event(("remove_user", 2))
        self.assertEqual(clusters, [{1}])

    def test_cluster_density_constraint(self):
        """Test that clusters maintain the minimum density constraint."""
        clustering = NetworkClustering(0.6)
        # Add 4 users
        for i in range(1, 5):
            clustering.process_event(("add_user", i))
        
        # Create a fully connected subgraph between users 1, 2, and 3
        clustering.process_event(("add_relationship", 1, 2))
        clustering.process_event(("add_relationship", 1, 3))
        clustering.process_event(("add_relationship", 2, 3))
        
        # Connect user 4 to user 1
        clusters = clustering.process_event(("add_relationship", 1, 4))
        
        # With min_density = 0.6, users 1, 2, 3, 4 cannot be in the same cluster
        # because the density would be (2*4)/(4*3) = 8/12 = 0.667, which is above 0.6
        # Or we might have two separate clusters
        
        # Check that all clusters meet the minimum density requirement
        for cluster in clusters:
            if len(cluster) >= 2:
                # Count edges within the cluster
                edges = 0
                for u in cluster:
                    for v in cluster:
                        if u < v:  # Avoid counting twice
                            # Check if relationship exists
                            temp_clusters = clustering.process_event(("remove_relationship", u, v))
                            if temp_clusters != clusters:  # If removing the edge changes clusters, it exists
                                edges += 1
                                clustering.process_event(("add_relationship", u, v))  # Add it back
                
                density = (2 * edges) / (len(cluster) * (len(cluster) - 1)) if len(cluster) > 1 else 0
                self.assertGreaterEqual(density, 0.6)
    
    def test_complex_scenario(self):
        """Test a more complex scenario with multiple events."""
        clustering = NetworkClustering(0.5)
        events = [
            ("add_user", 1),
            ("add_user", 2),
            ("add_relationship", 1, 2),
            ("add_user", 3),
            ("add_relationship", 1, 3),
            ("remove_relationship", 1, 2),
        ]
        
        expected_results = [
            [{1}],
            [{1}, {2}],
            [{1, 2}],
            [{1, 2}, {3}],
            [{1, 2, 3}],
            [{1, 3}, {2}],
        ]
        
        for i, event in enumerate(events):
            clusters = clustering.process_event(event)
            self.assertEqual(
                sorted([sorted(list(c)) for c in clusters]),
                sorted([sorted(list(c)) for c in expected_results[i]]),
                f"Failed at event {i}: {event}"
            )
    
    def test_edge_case_zero_density(self):
        """Test with zero minimum density - all users can be in the same cluster."""
        clustering = NetworkClustering(0.0)
        for i in range(1, 6):
            clustering.process_event(("add_user", i))
        
        clustering.process_event(("add_relationship", 1, 2))
        clusters = clustering.get_clusters()
        
        # With zero density, all users can be in the same cluster or separate ones
        # Just verify all users are present
        all_users = set()
        for cluster in clusters:
            all_users.update(cluster)
        self.assertEqual(all_users, {1, 2, 3, 4, 5})
    
    def test_edge_case_full_density(self):
        """Test with full density - clusters must be fully connected."""
        clustering = NetworkClustering(1.0)
        for i in range(1, 4):
            clustering.process_event(("add_user", i))
        
        # Add some relationships
        clustering.process_event(("add_relationship", 1, 2))
        clustering.process_event(("add_relationship", 2, 3))
        
        clusters = clustering.get_clusters()
        
        # With density 1.0, clusters can only contain users that are fully connected
        for cluster in clusters:
            if len(cluster) > 1:
                # Verify the cluster is fully connected
                for u in cluster:
                    for v in cluster:
                        if u != v:
                            # Check if the edge exists by trying to remove it
                            temp = clustering.process_event(("remove_relationship", u, v))
                            if temp == clusters:  # If unchanged, no edge existed
                                self.fail(f"Cluster {cluster} is not fully connected: no edge between {u} and {v}")
                            # Add it back
                            clustering.process_event(("add_relationship", u, v))
    
    def test_large_network(self):
        """Test with a larger network to ensure the algorithm scales."""
        clustering = NetworkClustering(0.3)
        
        # Add 100 users
        for i in range(1, 101):
            clustering.process_event(("add_user", i))
        
        # Add some relationships to form communities
        for i in range(1, 21):
            for j in range(i+1, 21):
                clustering.process_event(("add_relationship", i, j))
        
        for i in range(21, 41):
            for j in range(i+1, 41):
                clustering.process_event(("add_relationship", i, j))
        
        clusters = clustering.get_clusters()
        
        # Check that each cluster meets the minimum density requirement
        for cluster in clusters:
            if len(cluster) >= 2:
                # Count edges within the cluster
                edges = 0
                for u in cluster:
                    for v in cluster:
                        if u < v:
                            # Check if relationship exists
                            temp_clusters = clustering.process_event(("remove_relationship", u, v))
                            if temp_clusters != clusters:  # If removing the edge changes clusters, it exists
                                edges += 1
                                clustering.process_event(("add_relationship", u, v))  # Add it back
                
                density = (2 * edges) / (len(cluster) * (len(cluster) - 1)) if len(cluster) > 1 else 0
                self.assertGreaterEqual(density, 0.3)
    
    def test_get_clusters(self):
        """Test the get_clusters method."""
        clustering = NetworkClustering(0.5)
        clustering.process_event(("add_user", 1))
        clustering.process_event(("add_user", 2))
        clustering.process_event(("add_user", 3))
        clustering.process_event(("add_relationship", 1, 2))
        
        # Test get_clusters directly
        self.assertEqual(
            sorted([sorted(list(c)) for c in clustering.get_clusters()]),
            [[1, 2], [3]]
        )
        
        # Test get_clusters via process_event
        self.assertEqual(
            sorted([sorted(list(c)) for c in clustering.process_event(("get_clusters",))]),
            [[1, 2], [3]]
        )


if __name__ == "__main__":
    unittest.main()