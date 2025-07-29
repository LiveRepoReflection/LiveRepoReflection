import unittest
from network_optimizer import design_network

class TestNetworkOptimizer(unittest.TestCase):
    def test_basic_functionality(self):
        # Mock cost function for testing
        cost_matrix = [
            [0, 5, 8, 3],
            [5, 0, 2, 6],
            [8, 2, 0, 1],
            [3, 6, 1, 0]
        ]
        
        def mock_cost(i, j):
            return cost_matrix[i][j]
        
        # Basic test case with 4 nodes, 3 requests, max 2 connections per node
        N = 4
        M = 3
        K = 2
        communication_requests = [
            (0, 3, 50),  # Node 0 needs to send 50 units of data to node 3
            (1, 2, 30),  # Node 1 needs to send 30 units of data to node 2
            (0, 2, 20)   # Node 0 needs to send 20 units of data to node 2
        ]
        
        topology = design_network(N, M, K, communication_requests, mock_cost)
        
        # Verify that the topology is a list of tuples
        self.assertIsInstance(topology, list)
        for link in topology:
            self.assertIsInstance(link, tuple)
            self.assertEqual(len(link), 2)
        
        # Verify that each node has at most K connections
        node_connections = [0] * N
        for i, j in topology:
            node_connections[i] += 1
            node_connections[j] += 1
        
        for connections in node_connections:
            self.assertLessEqual(connections, K)
        
        # Create adjacency list to check connectivity
        adj_list = [[] for _ in range(N)]
        for i, j in topology:
            adj_list[i].append(j)
            adj_list[j].append(i)
        
        # Verify connectivity for each request
        for source, destination, _ in communication_requests:
            self.assertTrue(self.is_connected(adj_list, source, destination))
        
        # Calculate total cost
        total_cost = sum(mock_cost(i, j) for i, j in topology)
        self.assertGreaterEqual(total_cost, 0)  # Cost should be non-negative

    def test_edge_case_single_node(self):
        def mock_cost(i, j):
            return 1
        
        N = 1
        M = 0
        K = 0
        communication_requests = []
        
        topology = design_network(N, M, K, communication_requests, mock_cost)
        
        self.assertEqual(len(topology), 0)  # No connections needed

    def test_edge_case_max_connections(self):
        # Mock cost function that always returns 1
        def mock_cost(i, j):
            return 1
        
        N = 4
        M = 6
        K = 3
        
        # Create a fully connected graph requirement (every node needs to communicate with every other node)
        communication_requests = []
        for i in range(N):
            for j in range(i+1, N):
                communication_requests.append((i, j, 1))
        
        topology = design_network(N, M, K, communication_requests, mock_cost)
        
        # Check that no node exceeds K connections
        node_connections = [0] * N
        for i, j in topology:
            node_connections[i] += 1
            node_connections[j] += 1
        
        for connections in node_connections:
            self.assertLessEqual(connections, K)
        
        # Check connectivity
        adj_list = [[] for _ in range(N)]
        for i, j in topology:
            adj_list[i].append(j)
            adj_list[j].append(i)
        
        for i in range(N):
            for j in range(N):
                if i != j:
                    self.assertTrue(self.is_connected(adj_list, i, j))

    def test_large_network(self):
        def mock_cost(i, j):
            return (i * 17 + j * 13) % 100  # Some deterministic cost function
        
        N = 100
        M = 200
        K = 5
        
        import random
        random.seed(42)  # For reproducible tests
        
        communication_requests = []
        for _ in range(M):
            source = random.randint(0, N-1)
            destination = random.randint(0, N-1)
            while destination == source:  # Ensure different nodes
                destination = random.randint(0, N-1)
            data_size = random.randint(1, 100)
            communication_requests.append((source, destination, data_size))
        
        topology = design_network(N, M, K, communication_requests, mock_cost)
        
        # Check node connections limit
        node_connections = [0] * N
        for i, j in topology:
            node_connections[i] += 1
            node_connections[j] += 1
        
        for connections in node_connections:
            self.assertLessEqual(connections, K)
        
        # Create adjacency list
        adj_list = [[] for _ in range(N)]
        for i, j in topology:
            adj_list[i].append(j)
            adj_list[j].append(i)
        
        # Check connectivity for each request
        for source, destination, _ in communication_requests:
            self.assertTrue(self.is_connected(adj_list, source, destination))

    def test_cost_calls_optimization(self):
        # Test that the function minimizes calls to the cost function
        calls = 0
        
        def counting_cost(i, j):
            nonlocal calls
            calls += 1
            return i + j
        
        N = 10
        M = 15
        K = 3
        
        # Create simple communication requests
        communication_requests = []
        for i in range(M):
            source = i % N
            destination = (i + 3) % N
            data_size = 10
            communication_requests.append((source, destination, data_size))
        
        # Call the function and count how many times the cost function is called
        topology = design_network(N, M, K, communication_requests, counting_cost)
        
        # The maximum number of cost calls would be N*(N-1)/2 (for a complete graph)
        max_possible_calls = N * (N - 1) // 2
        self.assertLessEqual(calls, max_possible_calls)
        
        # Check that the topology meets requirements
        node_connections = [0] * N
        for i, j in topology:
            node_connections[i] += 1
            node_connections[j] += 1
        
        for connections in node_connections:
            self.assertLessEqual(connections, K)

    def is_connected(self, adj_list, source, destination):
        """Check if there is a path from source to destination using BFS."""
        if source == destination:
            return True
            
        visited = [False] * len(adj_list)
        queue = [source]
        visited[source] = True
        
        while queue:
            current = queue.pop(0)
            
            for neighbor in adj_list[current]:
                if neighbor == destination:
                    return True
                    
                if not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)
                    
        return False

if __name__ == '__main__':
    unittest.main()