import threading
import uuid
from collections import defaultdict

class MetadataServer:
    """
    MetadataServer maintains information about file chunks and their locations.
    It's responsible for managing file metadata and deciding where chunks should be stored.
    """
    def __init__(self):
        """Initialize the metadata server with empty data structures."""
        self.file_metadata = {}  # Maps file path to metadata
        self.lock = threading.RLock()  # Lock for thread safety
        self.next_node_index = 0  # For round-robin node selection
        
    def create_file_metadata(self, file_path, chunk_ids, num_nodes, replication_factor):
        """
        Create metadata for a new file.
        
        Args:
            file_path (str): Path to the file.
            chunk_ids (list): List of chunk IDs for this file.
            num_nodes (int): Total number of storage nodes.
            replication_factor (int): Number of replicas for each chunk.
            
        Returns:
            dict: The created file metadata.
        """
        with self.lock:
            chunk_locations = {}
            
            for chunk_id in chunk_ids:
                # Choose R different nodes for this chunk using round-robin
                selected_nodes = []
                for _ in range(replication_factor):
                    node_id = self.next_node_index
                    self.next_node_index = (self.next_node_index + 1) % num_nodes
                    selected_nodes.append(node_id)
                chunk_locations[chunk_id] = selected_nodes
            
            metadata = {
                "chunks": chunk_ids,  # List of chunk IDs in order
                "chunk_locations": chunk_locations  # Mapping of chunk ID to node IDs
            }
            
            self.file_metadata[file_path] = metadata
            return metadata
            
    def get_file_metadata(self, file_path):
        """
        Get metadata for an existing file.
        
        Args:
            file_path (str): Path to the file.
            
        Returns:
            dict: The file metadata.
            
        Raises:
            KeyError: If the file does not exist.
        """
        with self.lock:
            if file_path not in self.file_metadata:
                raise KeyError(f"File {file_path} not found")
            return self.file_metadata[file_path]