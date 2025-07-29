import concurrent.futures
import logging
from collections import defaultdict

def get_chunk_metadata(node_address):
    """
    Mock function to simulate getting chunk metadata from a storage node.
    In a real implementation, this would make network requests to the node.
    """
    raise NotImplementedError("This should be implemented with actual node communication")

def check_consistency(nodes, max_workers=5, retries=3):
    """
    Check consistency of chunks across multiple storage nodes in a DFS.
    
    Args:
        nodes: List of node addresses to check
        max_workers: Maximum number of concurrent workers for node queries
        retries: Number of retries for failed node queries
        
    Returns:
        List of inconsistency reports (dictionaries)
    """
    # Collect metadata from all nodes
    node_metadata = {}
    failed_nodes = set()
    
    for node in nodes:
        for attempt in range(retries):
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future = executor.submit(get_chunk_metadata, node)
                    node_metadata[node] = future.result()
                break
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed for node {node}: {str(e)}")
                if attempt == retries - 1:
                    failed_nodes.add(node)
                    logging.error(f"Failed to get metadata from node {node} after {retries} attempts")
    
    # Organize chunks by their ID for comparison
    chunk_data = defaultdict(list)
    
    for node, chunks in node_metadata.items():
        for chunk in chunks:
            chunk_data[chunk['chunk_id']].append((node, chunk))
    
    # Check for inconsistencies
    inconsistencies = []
    
    for chunk_id, node_chunks in chunk_data.items():
        if len(node_chunks) < 2:
            continue  # No replicas to compare
            
        # Get all versions and sizes for this chunk
        versions = {chunk['version'] for _, chunk in node_chunks}
        sizes = {chunk['size'] for _, chunk in node_chunks}
        
        if len(versions) > 1:
            inconsistencies.append({
                'chunk_id': chunk_id,
                'inconsistent_nodes': node_chunks,
                'reason': 'version mismatch'
            })
        elif len(sizes) > 1:
            inconsistencies.append({
                'chunk_id': chunk_id,
                'inconsistent_nodes': node_chunks,
                'reason': 'size mismatch'
            })
    
    return inconsistencies