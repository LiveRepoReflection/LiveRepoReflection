import unittest
from code_reorg import find_optimal_components

class CodeReorgTest(unittest.TestCase):
    def validate_solution(self, n, dependencies, k, components):
        # Check if every module is assigned to exactly one component
        all_modules = set()
        for component in components:
            all_modules.update(component)
        self.assertEqual(all_modules, set(range(n)), "All modules must be assigned to exactly one component")
        
        # Check if components don't overlap
        total_modules = sum(len(component) for component in components)
        self.assertEqual(total_modules, n, "Each module must be assigned to exactly one component")
        
        # Check component size limit
        for i, component in enumerate(components):
            self.assertLessEqual(len(component), k, f"Component {i} exceeds maximum size limit of {k}")
        
        # Check if component dependency graph is acyclic
        component_map = {}
        for i, component in enumerate(components):
            for module in component:
                component_map[module] = i
        
        component_dependencies = set()
        for u, v in dependencies:
            comp_u = component_map[u]
            comp_v = component_map[v]
            if comp_u != comp_v:
                component_dependencies.add((comp_u, comp_v))
        
        # Check if component dependency graph is acyclic
        visited = set()
        temp = set()
        
        def has_cycle(node):
            if node in temp:
                return True
            if node in visited:
                return False
            
            temp.add(node)
            
            for _, v in [(u, v) for u, v in component_dependencies if u == node]:
                if has_cycle(v):
                    return True
            
            temp.remove(node)
            visited.add(node)
            return False
        
        for i in range(len(components)):
            if i not in visited:
                if has_cycle(i):
                    self.fail("Component dependency graph contains cycles")
        
        # Count inter-component dependencies
        inter_component_deps = sum(1 for u, v in dependencies if component_map[u] != component_map[v])
        return inter_component_deps

    def test_simple_case(self):
        n = 6
        dependencies = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5)]
        k = 3
        
        components = find_optimal_components(n, len(dependencies), dependencies, k)
        inter_deps = self.validate_solution(n, dependencies, k, components)
        self.assertLessEqual(inter_deps, 6, "Solution should minimize inter-component dependencies")

    def test_linear_chain(self):
        n = 10
        dependencies = [(i, i+1) for i in range(n-1)]
        k = 3
        
        components = find_optimal_components(n, len(dependencies), dependencies, k)
        inter_deps = self.validate_solution(n, dependencies, k, components)
        # At minimum, we need to break the chain at least 3 times with 4 components
        self.assertLessEqual(inter_deps, 4, "Linear chain should be split efficiently")

    def test_star_pattern(self):
        n = 11
        # Node 0 is the center, connecting to all other nodes
        dependencies = [(0, i) for i in range(1, n)]
        k = 5
        
        components = find_optimal_components(n, len(dependencies), dependencies, k)
        inter_deps = self.validate_solution(n, dependencies, k, components)
        # With a star pattern, at most n-1 inter-component dependencies
        self.assertLessEqual(inter_deps, n-1, "Star pattern should be handled efficiently")

    def test_large_case(self):
        n = 100
        # Create a layered DAG - each node connects to next layer
        dependencies = []
        for layer in range(4):  # 4 layers
            for i in range(layer * 25, (layer + 1) * 25):  # 25 nodes per layer
                if layer < 3:  # Not for last layer
                    for j in range((layer + 1) * 25, (layer + 2) * 25):
                        dependencies.append((i, j))
        k = 30
        
        components = find_optimal_components(n, len(dependencies), dependencies, k)
        inter_deps = self.validate_solution(n, dependencies, k, components)
        # With 4 layers of 25 nodes each, and k=30, at least 3 components needed
        self.assertLessEqual(inter_deps, 2500, "Large layered DAG should be split efficiently")

    def test_disconnected_nodes(self):
        n = 12
        # Two separate star patterns
        dependencies = [(0, i) for i in range(1, 6)] + [(6, i) for i in range(7, 12)]
        k = 4
        
        components = find_optimal_components(n, len(dependencies), dependencies, k)
        inter_deps = self.validate_solution(n, dependencies, k, components)
        # Optimal: 3 components each for the two stars
        self.assertLessEqual(inter_deps, 10, "Disconnected components should be handled separately")

    def test_edge_case_k_equals_n(self):
        n = 5
        dependencies = [(0, 1), (1, 2), (2, 3), (3, 4)]
        k = n  # k equals n
        
        components = find_optimal_components(n, len(dependencies), dependencies, k)
        inter_deps = self.validate_solution(n, dependencies, k, components)
        # Optimal solution is to put all nodes in one component
        self.assertEqual(inter_deps, 0, "When K=N, all nodes should be in one component")

    def test_edge_case_k_equals_one(self):
        n = 5
        dependencies = [(0, 1), (1, 2), (2, 3), (3, 4)]
        k = 1  # k equals 1
        
        components = find_optimal_components(n, len(dependencies), dependencies, k)
        inter_deps = self.validate_solution(n, dependencies, k, components)
        # Each node must be in its own component
        self.assertEqual(inter_deps, 4, "When K=1, each node should be in its own component")

    def test_complex_dag(self):
        n = 15
        dependencies = [
            (0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6),
            (3, 7), (4, 7), (5, 8), (6, 8), (7, 9), (8, 9),
            (9, 10), (9, 11), (10, 12), (11, 13), (12, 14), (13, 14)
        ]
        k = 5
        
        components = find_optimal_components(n, len(dependencies), dependencies, k)
        inter_deps = self.validate_solution(n, dependencies, k, components)
        # Complex DAG with 15 nodes and k=5 should be split optimally
        self.assertLessEqual(inter_deps, 10, "Complex DAG should be split optimally")

if __name__ == "__main__":
    unittest.main()