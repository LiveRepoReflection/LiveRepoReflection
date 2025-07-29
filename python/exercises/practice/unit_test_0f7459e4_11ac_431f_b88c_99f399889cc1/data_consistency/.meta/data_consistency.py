from collections import defaultdict
from typing import List, Dict, Tuple, Any


def find_inconsistencies(data: List[Dict[int, int]]) -> List[Tuple[int, List[int], List[int]]]:
    """
    Find inconsistencies in a distributed file system.
    
    Args:
        data: A list of dictionaries, where each dictionary represents a node's data.
              The key is the chunk index and the value is the chunk's version number.
    
    Returns:
        A list of tuples, each containing:
        - chunk_index: The index of the inconsistent chunk.
        - node_ids: A list of node IDs that store this chunk.
        - version_numbers: A list of version numbers corresponding to the node_ids.
        
    Raises:
        TypeError: If input is not a list of dictionaries or if chunk indices or version numbers
                  are not integers.
    """
    # Validate input
    if not isinstance(data, list):
        raise TypeError("Input must be a list of dictionaries")
    
    # Group chunks by their index
    chunks = defaultdict(list)
    
    # Process each node
    for node_id, node_data in enumerate(data):
        if not isinstance(node_data, dict):
            raise TypeError(f"Node data at index {node_id} must be a dictionary")
        
        # Process each chunk in the node
        for chunk_idx, version in node_data.items():
            if not isinstance(chunk_idx, int) or not isinstance(version, int):
                raise TypeError(f"Chunk indices and version numbers must be integers (node {node_id})")
            
            # Store node_id and version for this chunk
            chunks[chunk_idx].append((node_id, version))
    
    # Find inconsistencies
    inconsistencies = []
    
    for chunk_idx, node_versions in chunks.items():
        # Skip if chunk is only on one node
        if len(node_versions) <= 1:
            continue
        
        # Check if all versions are the same
        versions = [v for _, v in node_versions]
        if len(set(versions)) > 1:
            # Inconsistency found
            node_ids = [node_id for node_id, _ in node_versions]
            inconsistencies.append((chunk_idx, node_ids, versions))
    
    return inconsistencies


def find_inconsistencies_optimized(data: List[Dict[int, int]]) -> List[Tuple[int, List[int], List[int]]]:
    """
    An optimized implementation for large datasets.
    
    This version uses more efficient data structures and processing logic
    for handling very large numbers of nodes and chunks.
    
    Args:
        data: A list of dictionaries representing node data.
    
    Returns:
        A list of inconsistency tuples.
    """
    if not isinstance(data, list):
        raise TypeError("Input must be a list of dictionaries")
    
    # First pass: identify all unique chunks and collect their versions
    chunk_versions = defaultdict(dict)  # {chunk_idx: {version: [node_ids]}}
    
    for node_id, node_data in enumerate(data):
        if not isinstance(node_data, dict):
            raise TypeError(f"Node data at index {node_id} must be a dictionary")
            
        for chunk_idx, version in node_data.items():
            if not isinstance(chunk_idx, int) or not isinstance(version, int):
                raise TypeError(f"Chunk indices and version numbers must be integers (node {node_id})")
                
            if version not in chunk_versions[chunk_idx]:
                chunk_versions[chunk_idx][version] = []
            chunk_versions[chunk_idx][version].append(node_id)
    
    # Second pass: identify inconsistencies
    inconsistencies = []
    
    for chunk_idx, versions_dict in chunk_versions.items():
        if len(versions_dict) > 1:  # More than one version exists for this chunk
            node_ids = []
            version_numbers = []
            
            for version, nodes in versions_dict.items():
                node_ids.extend(nodes)
                version_numbers.extend([version] * len(nodes))
                
            inconsistencies.append((chunk_idx, node_ids, version_numbers))
    
    return inconsistencies