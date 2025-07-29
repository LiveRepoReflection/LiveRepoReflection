import networkx as nx
import numpy as np
from collections import defaultdict
from itertools import combinations

def network_splitter(graph, k, alpha):
    """
    Partition a graph into k clusters optimizing the objective function:
    alpha * max_diameter + (1 - alpha) * normalized_cut_size
    
    Args:
        graph: NetworkX Graph object with weighted edges
        k: Number of desired clusters
        alpha: Weight parameter between 0 and 1
        
    Returns:
        Dictionary mapping nodes to cluster IDs (1 to k)
    """
    # Input validation
    if not isinstance(graph, nx.Graph):
        raise ValueError("Input must be a NetworkX Graph")
    if k < 1 or k > len(graph.nodes):
        raise ValueError(f"k must be between 1 and {len(graph.nodes)}")
    if alpha < 0 or alpha > 1:
        raise ValueError("alpha must be between 0 and 1")
    
    # Precompute all pairs shortest paths
    shortest_paths = dict(nx.all_pairs_dijkstra_path_length(graph))
    
    # Initialize clusters using spectral clustering
    clusters = initialize_spectral_clustering(graph, k)
    
    # Refine clusters using local search
    clusters = refine_clusters(graph, clusters, k, alpha, shortest_paths)
    
    return clusters

def initialize_spectral_clustering(graph, k):
    """
    Initialize clusters using spectral clustering
    """
    # Create Laplacian matrix
    laplacian = nx.laplacian_matrix(graph).astype(float)
    
    # Compute first k eigenvectors
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian.toarray())
    k_smallest_eigenvectors = eigenvectors[:, np.argsort(eigenvalues)[:k]]
    
    # Perform k-means clustering on eigenvectors
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=k, random_state=0).fit(k_smallest_eigenvectors)
    
    # Map nodes to clusters
    return {node: int(label+1) for node, label in zip(graph.nodes(), kmeans.labels_)}

def refine_clusters(graph, clusters, k, alpha, shortest_paths):
    """
    Refine clusters using local search to optimize objective function
    """
    improved = True
    while improved:
        improved = False
        for node in graph.nodes():
            current_cluster = clusters[node]
            
            # Evaluate current objective
            current_score = compute_objective(graph, clusters, k, alpha, shortest_paths)
            
            # Try moving node to each other cluster
            for new_cluster in range(1, k+1):
                if new_cluster == current_cluster:
                    continue
                
                # Temporarily move node
                clusters[node] = new_cluster
                new_score = compute_objective(graph, clusters, k, alpha, shortest_paths)
                
                # Keep change if improvement
                if new_score < current_score:
                    improved = True
                    current_score = new_score
                    current_cluster = new_cluster
                else:
                    # Revert change
                    clusters[node] = current_cluster
    
    return clusters

def compute_objective(graph, clusters, k, alpha, shortest_paths):
    """
    Compute the objective function value:
    alpha * max_diameter + (1 - alpha) * normalized_cut_size
    """
    # Compute max diameter
    max_diameter = 0
    for cluster_id in range(1, k+1):
        cluster_nodes = [n for n, c in clusters.items() if c == cluster_id]
        if len(cluster_nodes) <= 1:
            diameter = 0
        else:
            diameter = max(shortest_paths[u][v] 
                          for u, v in combinations(cluster_nodes, 2))
        max_diameter = max(max_diameter, diameter)
    
    # Compute normalized cut size
    cut_size = 0
    total_weight = sum(data['weight'] for _, _, data in graph.edges(data=True))
    
    for u, v, data in graph.edges(data=True):
        if clusters[u] != clusters[v]:
            cut_size += data['weight']
    
    normalized_cut_size = cut_size / total_weight if total_weight > 0 else 0
    
    return alpha * max_diameter + (1 - alpha) * normalized_cut_size