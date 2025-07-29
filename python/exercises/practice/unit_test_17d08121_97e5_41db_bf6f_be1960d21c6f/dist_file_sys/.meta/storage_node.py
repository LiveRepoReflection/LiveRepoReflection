import threading
import time

class StorageNode:
    """
    StorageNode represents a single storage node in the distributed file system.
    It's responsible for storing and retrieving chunks of data.
    """
    def __init__(self, node_id):
        """
        Initialize a StorageNode.
        
        Args:
            node_id (int): Unique identifier for this storage node.
        """
        self.node_id = node_id
        self.chunks = {}  # Dictionary mapping chunk_id to chunk data
        self.lock = threading.RLock()  # Lock for thread safety
        
    def write_chunk(self, chunk_id, data):
        """
        Write a chunk of data to the storage node.
        
        Args:
            chunk_id (str): Unique identifier for the chunk.
            data (bytes): The chunk data to be stored.
            
        Returns:
            bool: True if the write was successful, False otherwise.
        """
        with self.lock:
            try:
                self.chunks[chunk_id] = data
                return True
            except Exception as e:
                print(f"Error writing chunk {chunk_id} to node {self.node_id}: {str(e)}")
                return False
                
    def read_chunk(self, chunk_id):
        """
        Read a chunk of data from the storage node.
        
        Args:
            chunk_id (str): Unique identifier for the chunk to read.
            
        Returns:
            bytes: The chunk data if found.
            
        Raises:
            KeyError: If the chunk is not found on this node.
        """
        with self.lock:
            if chunk_id not in self.chunks:
                raise KeyError(f"Chunk {chunk_id} not found on node {self.node_id}")
            return self.chunks[chunk_id]