import heapq
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Set, Optional


class IntergalacticRouter:
    """
    A routing system for the Intergalactic Federation's network of interconnected planets.
    """
    
    def __init__(self, planets: List[int], subnets: List[int], 
                 planet_to_subnets: Dict[int, List[int]],
                 subnet_graphs: Dict[int, Dict[int, List[Tuple[int, float]]]], 
                 transfer_cost: float):
        """
        Initialize the router with the network configuration.
        
        Args:
            planets: List of planet IDs
            subnets: List of subnet IDs
            planet_to_subnets: Mapping of planets to the subnets they belong to
            subnet_graphs: Mapping of subnets to their graph representation
            transfer_cost: Cost of transferring between subnets
        """
        self.planets = set(planets)
        self.subnets = set(subnets)
        self.planet_to_subnets = planet_to_subnets
        self.subnet_graphs = subnet_graphs
        self.transfer_cost = transfer_cost
        
        # Validate the initial configuration
        self._validate_configuration()
        
        # Build the combined graph representation for efficient routing
        self._build_multilayer_graph()
    
    def _validate_configuration(self) -> None:
        """
        Validates the initial network configuration.
        
        Raises:
            ValueError: If the configuration is invalid.
        """
        # Check that all planets have subnet assignments
        for planet in self.planets:
            if planet not in self.planet_to_subnets:
                raise ValueError(f"Planet {planet} has no subnet assignments")
        
        # Check that all subnet assignments are valid
        for planet, assigned_subnets in self.planet_to_subnets.items():
            if not all(subnet in self.subnets for subnet in assigned_subnets):
                raise ValueError(f"Planet {planet} has invalid subnet assignments")
        
        # Check that subnet graphs are consistent
        for subnet, graph in self.subnet_graphs.items():
            if subnet not in self.subnets:
                raise ValueError(f"Subnet {subnet} is not in the subnets list")
            
            for planet, neighbors in graph.items():
                # Check that the planet belongs to this subnet
                if subnet not in self.planet_to_subnets.get(planet, []):
                    raise ValueError(f"Planet {planet} in subnet graph {subnet} does not belong to that subnet")
                
                # Check that all neighbors are valid
                for neighbor, cost in neighbors:
                    if neighbor not in self.planets:
                        raise ValueError(f"Invalid neighbor {neighbor} for planet {planet} in subnet {subnet}")
                    if cost < 0:
                        raise ValueError(f"Negative cost {cost} for edge ({planet}, {neighbor}) in subnet {subnet}")
                    if subnet not in self.planet_to_subnets.get(neighbor, []):
                        raise ValueError(f"Neighbor {neighbor} of planet {planet} in subnet graph {subnet} does not belong to that subnet")
    
    def _build_multilayer_graph(self) -> None:
        """
        Builds a multi-layer graph representation of the network for efficient routing.
        A node in this graph is a (planet, subnet) pair.
        """
        self.multilayer_graph = defaultdict(list)
        
        # Add edges within subnets
        for subnet, graph in self.subnet_graphs.items():
            for planet, neighbors in graph.items():
                for neighbor, cost in neighbors:
                    # Add directed edge: (planet, subnet) -> (neighbor, subnet) with cost
                    self.multilayer_graph[(planet, subnet)].append(((neighbor, subnet), cost))
        
        # Add "virtual" edges for subnet transitions (when a planet belongs to multiple subnets)
        for planet in self.planets:
            subnets = self.planet_to_subnets.get(planet, [])
            if len(subnets) > 1:
                for i, subnet1 in enumerate(subnets):
                    for subnet2 in subnets[i+1:]:
                        # Add bidirectional edges with transfer cost
                        self.multilayer_graph[(planet, subnet1)].append(((planet, subnet2), self.transfer_cost))
                        self.multilayer_graph[(planet, subnet2)].append(((planet, subnet1), self.transfer_cost))
    
    def update_edge_costs(self, edge_updates: List[Tuple[int, int, int, float]]) -> None:
        """
        Updates the costs of edges in the network.
        
        Args:
            edge_updates: List of tuples (subnet_id, planet_id1, planet_id2, new_cost)
        """
        for subnet, planet1, planet2, new_cost in edge_updates:
            if subnet not in self.subnets:
                raise ValueError(f"Invalid subnet ID: {subnet}")
            
            # Validate planets
            if planet1 not in self.planets or planet2 not in self.planets:
                raise ValueError(f"Invalid planet ID(s): {planet1}, {planet2}")
            
            # Check if these planets belong to the given subnet
            if subnet not in self.planet_to_subnets.get(planet1, []) or subnet not in self.planet_to_subnets.get(planet2, []):
                raise ValueError(f"One or both planets ({planet1}, {planet2}) do not belong to subnet {subnet}")
            
            if new_cost < 0:
                raise ValueError(f"Edge cost cannot be negative: {new_cost}")
            
            # Update the edge in the subnet graph (for both directions in undirected graph)
            self._update_subnet_edge(subnet, planet1, planet2, new_cost)
            self._update_subnet_edge(subnet, planet2, planet1, new_cost)
            
            # Update the multilayer graph
            self._update_multilayer_edge((planet1, subnet), (planet2, subnet), new_cost)
            self._update_multilayer_edge((planet2, subnet), (planet1, subnet), new_cost)
    
    def _update_subnet_edge(self, subnet: int, planet1: int, planet2: int, new_cost: float) -> None:
        """
        Updates an edge in the subnet graph.
        
        Args:
            subnet: Subnet ID
            planet1: Source planet ID
            planet2: Destination planet ID
            new_cost: New cost of the edge
        """
        if planet1 in self.subnet_graphs[subnet]:
            # Find and update the edge
            for i, (p, _) in enumerate(self.subnet_graphs[subnet][planet1]):
                if p == planet2:
                    self.subnet_graphs[subnet][planet1][i] = (planet2, new_cost)
                    return
            
            # Edge doesn't exist yet, add it
            self.subnet_graphs[subnet][planet1].append((planet2, new_cost))
        else:
            # Planet doesn't have any edges yet
            self.subnet_graphs[subnet][planet1] = [(planet2, new_cost)]
    
    def _update_multilayer_edge(self, node1: Tuple[int, int], node2: Tuple[int, int], new_cost: float) -> None:
        """
        Updates an edge in the multilayer graph.
        
        Args:
            node1: Source node (planet, subnet)
            node2: Destination node (planet, subnet)
            new_cost: New cost of the edge
        """
        for i, (neighbor, _) in enumerate(self.multilayer_graph[node1]):
            if neighbor == node2:
                self.multilayer_graph[node1][i] = (node2, new_cost)
                return
        
        # Edge doesn't exist yet, add it
        self.multilayer_graph[node1].append((node2, new_cost))
    
    def find_optimal_path(self, source_planet: int, destination_planet: int) -> Tuple[Optional[List[int]], float]:
        """
        Finds the optimal path between two planets.
        
        Args:
            source_planet: Source planet ID
            destination_planet: Destination planet ID
            
        Returns:
            A tuple (path, cost) where path is a list of planet IDs forming the optimal path,
            and cost is the total cost of that path. If no path exists, returns (None, float('inf')).
        """
        # Handle special cases
        if source_planet == destination_planet:
            return [source_planet], 0.0
        
        if source_planet not in self.planets or destination_planet not in self.planets:
            return None, float('inf')
        
        # Get the subnets that contain the source and destination planets
        source_subnets = self.planet_to_subnets.get(source_planet, [])
        dest_subnets = self.planet_to_subnets.get(destination_planet, [])
        
        if not source_subnets or not dest_subnets:
            return None, float('inf')
        
        # Run Dijkstra's algorithm on the multilayer graph
        return self._find_dijkstra_path(source_planet, destination_planet, source_subnets, dest_subnets)
    
    def _find_dijkstra_path(self, source_planet: int, destination_planet: int, 
                           source_subnets: List[int], dest_subnets: List[int]) -> Tuple[Optional[List[int]], float]:
        """
        Implements Dijkstra's algorithm on the multilayer graph.
        
        Args:
            source_planet: Source planet ID
            destination_planet: Destination planet ID
            source_subnets: Subnets containing the source planet
            dest_subnets: Subnets containing the destination planet
            
        Returns:
            A tuple (path, cost) where path is a list of planet IDs forming the optimal path,
            and cost is the total cost of that path. If no path exists, returns (None, float('inf')).
        """
        # Initialize distances and visited sets
        distances = {}
        predecessors = {}
        visited = set()
        
        # Priority queue for Dijkstra's algorithm
        pq = []
        
        # Add all source nodes to the queue
        for subnet in source_subnets:
            source_node = (source_planet, subnet)
            distances[source_node] = 0
            heapq.heappush(pq, (0, source_node))
        
        # Dijkstra's algorithm
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            # If we've already processed this node, skip
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            current_planet, current_subnet = current_node
            
            # If we've reached the destination planet in any subnet, we can potentially stop
            if current_planet == destination_planet and current_subnet in dest_subnets:
                # Reconstruct the path
                path = self._reconstruct_path(predecessors, source_planet, destination_planet, 
                                             source_subnets, current_node)
                return path, current_dist
            
            # Explore neighbors
            for neighbor_node, edge_cost in self.multilayer_graph[current_node]:
                if neighbor_node in visited:
                    continue
                
                new_dist = current_dist + edge_cost
                if neighbor_node not in distances or new_dist < distances[neighbor_node]:
                    distances[neighbor_node] = new_dist
                    predecessors[neighbor_node] = current_node
                    heapq.heappush(pq, (new_dist, neighbor_node))
        
        # If we got here, no path was found
        return None, float('inf')
    
    def _reconstruct_path(self, predecessors: Dict[Tuple[int, int], Tuple[int, int]], 
                         source_planet: int, destination_planet: int, 
                         source_subnets: List[int], final_node: Tuple[int, int]) -> List[int]:
        """
        Reconstructs the planet path from the predecessors dictionary.
        
        Args:
            predecessors: Dictionary mapping nodes to their predecessors
            source_planet: Source planet ID
            destination_planet: Destination planet ID
            source_subnets: Subnets containing the source planet
            final_node: The final (planet, subnet) node reached
            
        Returns:
            A list of planet IDs forming the path from source to destination
        """
        # Start from the destination and work backwards
        path_nodes = []
        current_node = final_node
        
        while current_node[0] != source_planet or current_node[1] not in source_subnets:
            path_nodes.append(current_node)
            if current_node not in predecessors:
                # This shouldn't happen if Dijkstra found a path, but just in case
                return None
            current_node = predecessors[current_node]
        
        path_nodes.append(current_node)  # Add the source node
        
        # Reverse the path and extract just the planets (removing duplicate planets when switching subnets)
        path_planets = [source_planet]
        prev_planet = source_planet
        
        # Process nodes in reverse order (from source to destination)
        for node in reversed(path_nodes[:-1]):  # Skip the first node which is already added
            planet, _ = node
            if planet != prev_planet:
                path_planets.append(planet)
                prev_planet = planet
        
        return path_planets