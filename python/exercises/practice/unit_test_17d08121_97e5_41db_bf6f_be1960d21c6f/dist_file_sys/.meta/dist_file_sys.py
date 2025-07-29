import io
import threading
import time
import uuid
from io import BytesIO

class DistributedFileSystem:
    """
    DistributedFileSystem coordinates the storage nodes and metadata server
    to provide file read and write operations.
    """
    # Default chunk size (64MB in bytes)
    DEFAULT_CHUNK_SIZE = 64 * 1024 * 1024
    
    # Default read timeout for storage nodes (in seconds)
    DEFAULT_READ_TIMEOUT = 5.0
    
    def __init__(self, storage_nodes, metadata_server, replication_factor, 
                 chunk_size=None, read_timeout=None):
        """
        Initialize the distributed file system.
        
        Args:
            storage_nodes (list): List of StorageNode objects.
            metadata_server (MetadataServer): The metadata server instance.
            replication_factor (int): Number of replicas for each chunk.
            chunk_size (int, optional): Chunk size in bytes. Default is 64MB.
            read_timeout (float, optional): Timeout for read operations in seconds. Default is 5.0.
        """
        self.storage_nodes = storage_nodes
        self.metadata_server = metadata_server
        self.replication_factor = replication_factor
        self.chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
        self.read_timeout = read_timeout or self.DEFAULT_READ_TIMEOUT
        self.lock = threading.RLock()
        
        # Validate replication factor
        if replication_factor < 1 or replication_factor > len(storage_nodes):
            raise ValueError(f"Replication factor must be between 1 and {len(storage_nodes)}")
            
    def write(self, file_path, file_data):
        """
        Write a file to the distributed file system.
        
        Args:
            file_path (str): Path where the file should be stored.
            file_data (file-like object): File data to be written.
            
        Returns:
            bool: True if the write was successful, False otherwise.
            
        Raises:
            Exception: If the write operation fails.
        """
        with self.lock:
            try:
                # Split the file into chunks
                chunks = []
                chunk_ids = []
                
                while True:
                    chunk = file_data.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    chunk_id = f"{file_path}_{uuid.uuid4()}"
                    chunks.append(chunk)
                    chunk_ids.append(chunk_id)
                
                # Create file metadata
                metadata = self.metadata_server.create_file_metadata(
                    file_path, chunk_ids, len(self.storage_nodes), self.replication_factor
                )
                
                # Store each chunk on the selected nodes
                for i, chunk_id in enumerate(chunk_ids):
                    node_ids = metadata["chunk_locations"][chunk_id]
                    
                    # Try to write to all selected nodes
                    success_count = 0
                    for node_id in node_ids:
                        if self.storage_nodes[node_id].write_chunk(chunk_id, chunks[i]):
                            success_count += 1
                    
                    # If we couldn't write to enough nodes, fail the write operation
                    if success_count == 0:
                        raise Exception(f"Failed to write chunk {chunk_id} to any node")
                
                return True
                
            except Exception as e:
                # In a real system, we might want to clean up partially written chunks here
                raise Exception(f"Failed to write file {file_path}: {str(e)}")
    
    def read(self, file_path):
        """
        Read a file from the distributed file system.
        
        Args:
            file_path (str): Path of the file to read.
            
        Returns:
            BytesIO: File data as a file-like object.
            
        Raises:
            Exception: If the read operation fails or the file does not exist.
        """
        try:
            # Get metadata for the file
            metadata = self.metadata_server.get_file_metadata(file_path)
            chunk_ids = metadata["chunks"]
            
            # Read all chunks and combine them
            output = BytesIO()
            
            for chunk_id in chunk_ids:
                chunk_data = self._read_chunk_with_retry(chunk_id, metadata["chunk_locations"][chunk_id])
                output.write(chunk_data)
            
            output.seek(0)
            return output
            
        except KeyError as e:
            raise Exception(f"File {file_path} not found")
        except Exception as e:
            raise Exception(f"Failed to read file {file_path}: {str(e)}")
    
    def _read_chunk_with_retry(self, chunk_id, node_ids):
        """
        Read a chunk with retries across multiple nodes.
        
        Args:
            chunk_id (str): ID of the chunk to read.
            node_ids (list): List of node IDs where the chunk is stored.
            
        Returns:
            bytes: Chunk data.
            
        Raises:
            Exception: If the chunk cannot be read from any node.
        """
        # Shuffle node_ids to balance load
        import random
        nodes_to_try = node_ids.copy()
        random.shuffle(nodes_to_try)
        
        errors = []
        
        for node_id in nodes_to_try:
            try:
                # Try to read the chunk from this node
                return self.storage_nodes[node_id].read_chunk(chunk_id)
            except Exception as e:
                errors.append(f"Node {node_id}: {str(e)}")
                continue
        
        # If we reach here, we couldn't read the chunk from any node
        raise Exception(f"Failed to read chunk {chunk_id} from any node: {', '.join(errors)}")