import hashlib
import threading
import copy
from typing import Dict, List, Set, Tuple, Optional

class NodeData:
    def __init__(self, data_blocks: Dict[str, bytes], checksums: Dict[str, str]):
        self.data_blocks = data_blocks
        self.checksums = checksums


def detect_and_correct_corruption(N: int, node_data: Dict[int, NodeData], 
                                  suspected_nodes: List[int]) -> Tuple[Dict[int, NodeData], List[str]]:
    """
    Detects and corrects corrupted data blocks across a distributed system.
    
    Args:
        N: Total number of nodes in the system
        node_data: Dictionary mapping node IDs to their corresponding NodeData
        suspected_nodes: List of node IDs suspected of having corrupted data
        
    Returns:
        Tuple containing:
        - Updated node_data dictionary after corruption correction
        - List of UUIDs for unrecoverable data blocks
    """
    # Create a deep copy to avoid modifying the original data
    result_data = copy.deepcopy(node_data)
    
    # Thread-safe structures
    lock = threading.RLock()
    unrecoverable_blocks: Set[str] = set()
    
    # Get all unique block UUIDs across all nodes
    all_block_uuids: Set[str] = set()
    for node_id in range(N):
        if node_id in node_data:
            all_block_uuids.update(node_data[node_id].data_blocks.keys())
    
    # Function to process a single block
    def process_block(block_uuid):
        # Step 1: Collect checksums from all nodes for this block
        checksums_by_node = {}
        nodes_with_block = []
        for node_id in range(N):
            if node_id in node_data and block_uuid in node_data[node_id].data_blocks:
                nodes_with_block.append(node_id)
                stored_checksum = node_data[node_id].checksums.get(block_uuid)
                checksums_by_node[node_id] = stored_checksum
        
        # Step 2: Calculate actual checksums for suspected nodes
        actual_checksums = {}
        corrupted_nodes = []
        for node_id in suspected_nodes:
            if node_id in nodes_with_block:
                block_data = node_data[node_id].data_blocks[block_uuid]
                actual_checksum = hashlib.sha256(block_data).hexdigest()
                stored_checksum = checksums_by_node[node_id]
                
                if actual_checksum != stored_checksum:
                    corrupted_nodes.append(node_id)
                
                actual_checksums[node_id] = actual_checksum
        
        # If no corrupted nodes found for this block, return early
        if not corrupted_nodes:
            return
        
        # Step 3: Find most common checksum across all non-suspected nodes
        checksum_counts = {}
        for node_id in nodes_with_block:
            if node_id not in suspected_nodes:
                checksum = checksums_by_node[node_id]
                checksum_counts[checksum] = checksum_counts.get(checksum, 0) + 1
        
        # Also include actual checksums from suspected but not corrupted nodes
        for node_id in suspected_nodes:
            if node_id in nodes_with_block and node_id not in corrupted_nodes:
                checksum = checksums_by_node[node_id]
                checksum_counts[checksum] = checksum_counts.get(checksum, 0) + 1
        
        # Find the most common checksum and node with lowest ID that has this checksum
        correct_checksum = None
        correct_node_id = None
        max_count = 0
        
        for checksum, count in checksum_counts.items():
            if count > max_count:
                max_count = count
                correct_checksum = checksum
        
        # If we found a correct checksum, find lowest node ID with it
        if correct_checksum:
            for node_id in sorted(nodes_with_block):
                if node_id in checksums_by_node and checksums_by_node[node_id] == correct_checksum:
                    # Verify the data matches the checksum for non-suspected nodes
                    if node_id not in suspected_nodes:
                        correct_node_id = node_id
                        break
                    # For suspected nodes, verify the actual checksum
                    elif node_id in actual_checksums and actual_checksums[node_id] == correct_checksum:
                        correct_node_id = node_id
                        break
        
        # Step 4: Repair corrupted blocks or mark as unrecoverable
        with lock:
            if correct_node_id is not None:
                correct_data = node_data[correct_node_id].data_blocks[block_uuid]
                # Repair all corrupted nodes
                for node_id in corrupted_nodes:
                    result_data[node_id].data_blocks[block_uuid] = correct_data
                    result_data[node_id].checksums[block_uuid] = correct_checksum
            else:
                # Mark as unrecoverable
                unrecoverable_blocks.add(block_uuid)
    
    # Process blocks in parallel using threads
    threads = []
    for block_uuid in all_block_uuids:
        thread = threading.Thread(target=process_block, args=(block_uuid,))
        threads.append(thread)
        thread.start()
        
        # Limit concurrent threads to avoid system overload
        if len(threads) >= 100:  # Adjust based on system capabilities
            for t in threads:
                t.join()
            threads = []
    
    # Join any remaining threads
    for thread in threads:
        thread.join()
    
    return result_data, list(unrecoverable_blocks)