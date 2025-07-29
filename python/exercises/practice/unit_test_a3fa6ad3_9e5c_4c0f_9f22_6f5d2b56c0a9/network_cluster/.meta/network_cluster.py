import networkx as nx


class NetworkClustering:
    def __init__(self, min_density: float):
        """
        Initialize the NetworkClustering class with a minimum density requirement.
        
        Args:
            min_density: A float between 0 and 1 representing the minimum density required for a cluster.
        """
        self.min_density = min_density
        self.graph = nx.Graph()
        self.clusters = []  # List of sets, where each set is a cluster of user_ids
    
    def process_event(self, event: tuple) -> list[set[int]]:
        """
        Process an event and return the current list of clusters.
        
        Args:
            event: A tuple representing an event. The first element is the event type.
                  Possible event types are:
                  - ("add_user", user_id)
                  - ("remove_user", user_id)
                  - ("add_relationship", user_id1, user_id2)
                  - ("remove_relationship", user_id1, user_id2)
                  - ("get_clusters",)
        
        Returns:
            A list of sets, where each set represents a cluster of user_ids.
        """
        event_type = event[0]
        
        if event_type == "add_user":
            user_id = event[1]
            self._add_user(user_id)
        elif event_type == "remove_user":
            user_id = event[1]
            self._remove_user(user_id)
        elif event_type == "add_relationship":
            user_id1, user_id2 = event[1], event[2]
            self._add_relationship(user_id1, user_id2)
        elif event_type == "remove_relationship":
            user_id1, user_id2 = event[1], event[2]
            self._remove_relationship(user_id1, user_id2)
        elif event_type == "get_clusters":
            pass  # Just return current clusters
        
        return self.get_clusters()
    
    def get_clusters(self) -> list[set[int]]:
        """
        Return the current list of clusters.
        
        Returns:
            A list of sets, where each set represents a cluster of user_ids.
        """
        # Convert node clusters to sets
        return [set(cluster) for cluster in self.clusters]
    
    def _add_user(self, user_id: int) -> None:
        """
        Add a user to the network.
        
        Args:
            user_id: The ID of the user to add.
        """
        if user_id not in self.graph:
            self.graph.add_node(user_id)
            # Add the user as a single-node cluster
            self.clusters.append([user_id])
    
    def _remove_user(self, user_id: int) -> None:
        """
        Remove a user from the network.
        
        Args:
            user_id: The ID of the user to remove.
        """
        if user_id in self.graph:
            self.graph.remove_node(user_id)
            # Remove the user from clusters
            for cluster in self.clusters[:]:
                if user_id in cluster:
                    cluster.remove(user_id)
                    if not cluster:  # If cluster becomes empty, remove it
                        self.clusters.remove(cluster)
            
            # Recalculate clusters for affected components
            self._recalculate_clusters()
    
    def _add_relationship(self, user_id1: int, user_id2: int) -> None:
        """
        Add a relationship between two users.
        
        Args:
            user_id1: The ID of the first user.
            user_id2: The ID of the second user.
        """
        if user_id1 in self.graph and user_id2 in self.graph and not self.graph.has_edge(user_id1, user_id2):
            self.graph.add_edge(user_id1, user_id2)
            
            # Find clusters containing these users
            cluster1 = None
            cluster2 = None
            for cluster in self.clusters:
                if user_id1 in cluster:
                    cluster1 = cluster
                if user_id2 in cluster:
                    cluster2 = cluster
                if cluster1 and cluster2:
                    break
            
            # If users are in different clusters, try to merge them
            if cluster1 != cluster2:
                merged_cluster = list(set(cluster1 + cluster2))
                # Check if the merged cluster meets the density requirement
                if self._calculate_density(merged_cluster) >= self.min_density:
                    self.clusters.remove(cluster1)
                    self.clusters.remove(cluster2)
                    self.clusters.append(merged_cluster)
            
            # Recalculate clusters to ensure all density requirements are met
            self._recalculate_clusters()
    
    def _remove_relationship(self, user_id1: int, user_id2: int) -> None:
        """
        Remove a relationship between two users.
        
        Args:
            user_id1: The ID of the first user.
            user_id2: The ID of the second user.
        """
        if user_id1 in self.graph and user_id2 in self.graph and self.graph.has_edge(user_id1, user_id2):
            self.graph.remove_edge(user_id1, user_id2)
            
            # Recalculate clusters
            self._recalculate_clusters()
    
    def _calculate_density(self, nodes: list) -> float:
        """
        Calculate the density of a cluster.
        
        Args:
            nodes: A list of node IDs.
        
        Returns:
            The density of the cluster.
        """
        if len(nodes) < 2:
            return 0.0
        
        subgraph = self.graph.subgraph(nodes)
        n = subgraph.number_of_nodes()
        e = subgraph.number_of_edges()
        
        return (2 * e) / (n * (n - 1)) if n > 1 else 0.0
    
    def _recalculate_clusters(self) -> None:
        """
        Recalculate all clusters to ensure they meet the density requirement.
        This uses a greedy algorithm to split or merge clusters as needed.
        """
        # Start with connected components
        components = [list(comp) for comp in nx.connected_components(self.graph)]
        
        new_clusters = []
        for component in components:
            if not component:
                continue
                
            # If the component is a single node or meets the density requirement, keep it as is
            if len(component) == 1 or self._calculate_density(component) >= self.min_density:
                new_clusters.append(component)
                continue
            
            # Otherwise, try to split it into denser clusters
            clusters_from_component = self._split_component(component)
            new_clusters.extend(clusters_from_component)
        
        # Try to merge clusters if possible
        merged = True
        while merged:
            merged = False
            for i in range(len(new_clusters)):
                if merged:
                    break
                for j in range(i + 1, len(new_clusters)):
                    combined = list(set(new_clusters[i] + new_clusters[j]))
                    # Check if there's at least one edge between the clusters
                    has_edge = False
                    for u in new_clusters[i]:
                        for v in new_clusters[j]:
                            if self.graph.has_edge(u, v):
                                has_edge = True
                                break
                        if has_edge:
                            break
                    
                    if has_edge and self._calculate_density(combined) >= self.min_density:
                        new_clusters[i] = combined
                        new_clusters.pop(j)
                        merged = True
                        break
        
        self.clusters = new_clusters
    
    def _split_component(self, component: list) -> list[list]:
        """
        Split a component into clusters that satisfy the density requirement.
        
        Args:
            component: A list of node IDs.
        
        Returns:
            A list of clusters (each cluster is a list of node IDs).
        """
        # If the component is small or already dense enough, keep it as is
        if len(component) <= 2 or self._calculate_density(component) >= self.min_density:
            return [component]
        
        # Create a subgraph of the component
        subgraph = self.graph.subgraph(component)
        
        # Try community detection algorithms to find dense clusters
        # Using Girvan-Newman algorithm for hierarchical clustering
        communities_generator = nx.community.girvan_newman(subgraph)
        
        # Try different levels of clustering until we find one where all clusters meet the density requirement
        for communities in communities_generator:
            # Convert communities to lists
            communities_list = [list(community) for community in communities]
            
            # Check if all communities meet the density requirement
            all_meet_requirement = True
            for comm in communities_list:
                if self._calculate_density(comm) < self.min_density:
                    all_meet_requirement = False
                    break
            
            if all_meet_requirement:
                return communities_list
            
            # If we have too many singleton communities, stop
            singleton_count = sum(1 for comm in communities_list if len(comm) == 1)
            if singleton_count > len(component) / 2:
                break
        
        # If we couldn't find a good clustering, try a greedy approach
        return self._greedy_clustering(component)
    
    def _greedy_clustering(self, nodes: list) -> list[list]:
        """
        Use a greedy approach to cluster nodes.
        
        Args:
            nodes: A list of node IDs.
        
        Returns:
            A list of clusters (each cluster is a list of node IDs).
        """
        result = []
        remaining = set(nodes)
        
        while remaining:
            # Start with a random node
            current_cluster = [next(iter(remaining))]
            remaining.remove(current_cluster[0])
            
            # Greedily add nodes to the cluster if density remains above threshold
            added = True
            while added and remaining:
                added = False
                best_node = None
                best_density = -1
                
                for node in remaining:
                    test_cluster = current_cluster + [node]
                    density = self._calculate_density(test_cluster)
                    
                    if density >= self.min_density and density > best_density:
                        best_node = node
                        best_density = density
                
                if best_node:
                    current_cluster.append(best_node)
                    remaining.remove(best_node)
                    added = True
            
            result.append(current_cluster)
        
        return result