import math
import random
import threading

CHUNK_SIZE = 4096

class DistributedFileSystem:
    def __init__(self, num_storage_nodes: int, replication_factor: int):
        """
        Initializes the distributed file system.
        Args:
            num_storage_nodes: The number of storage nodes in the system.
            replication_factor: The number of replicas for each chunk.
        """
        self.num_storage_nodes = num_storage_nodes
        self.replication_factor = replication_factor
        # Simulate storage nodes: each node is represented as a dictionary mapping a chunk identifier to chunk data.
        self.storage_nodes = {node_id: {} for node_id in range(num_storage_nodes)}
        # Metadata store for files: key is file_path, value is a dict with 'size' and 'chunks'
        # 'chunks' is a list of dictionaries. Each dictionary has 'chunk_index' and 'nodes': list of node ids storing the chunk.
        self.metadata_store = {}
        # Locks for concurrency, one lock per file to protect write access
        self.file_locks = {}
        # Global lock to protect metadata and file_locks dictionaries during file creation and deletion
        self.global_lock = threading.Lock()

    def _is_valid_path(self, file_path: str) -> bool:
        # A valid file path must start with '/'
        return isinstance(file_path, str) and file_path.startswith("/") and len(file_path) > 1

    def create_file(self, file_path: str) -> bool:
        """
        Creates an empty file at the given file path.
        Returns:
            True if the file was successfully created, False otherwise.
        """
        if not self._is_valid_path(file_path):
            return False

        with self.global_lock:
            if file_path in self.metadata_store:
                return False
            # Initialize file metadata: size = 0 and empty list for chunks
            self.metadata_store[file_path] = {
                'size': 0,
                'chunks': []
            }
            # Initialize a lock for the file
            self.file_locks[file_path] = threading.Lock()
        return True

    def write_file(self, file_path: str, data: bytes) -> bool:
        """
        Writes the given data to the file at the given file path. Overwrites existing content.
        Returns:
            True if the data was successfully written, False otherwise.
        """
        if not self._is_valid_path(file_path):
            return False

        with self.global_lock:
            if file_path not in self.metadata_store:
                return False
            file_lock = self.file_locks[file_path]

        with file_lock:
            # First, remove any existing chunks associated with this file.
            old_metadata = self.metadata_store[file_path]
            for chunk_info in old_metadata.get('chunks', []):
                nodes = chunk_info.get('nodes', [])
                chunk_id = self._get_chunk_identifier(file_path, chunk_info['chunk_index'])
                for node in nodes:
                    if chunk_id in self.storage_nodes[node]:
                        del self.storage_nodes[node][chunk_id]

            # Now proceed to write new data.
            file_size = len(data)
            total_chunks = math.ceil(file_size / CHUNK_SIZE)
            new_chunks_metadata = []

            for chunk_index in range(total_chunks):
                start = chunk_index * CHUNK_SIZE
                end = start + CHUNK_SIZE
                chunk_data = data[start:end]

                # Ensure enough nodes exist for replication.
                if self.replication_factor > self.num_storage_nodes:
                    return False

                # Randomly select replication_factor distinct nodes.
                nodes_for_chunk = random.sample(range(self.num_storage_nodes), self.replication_factor)

                # Store the chunk in the selected nodes.
                chunk_id = self._get_chunk_identifier(file_path, chunk_index)
                for node in nodes_for_chunk:
                    self.storage_nodes[node][chunk_id] = chunk_data

                # Save metadata for this chunk.
                new_chunks_metadata.append({
                    'chunk_index': chunk_index,
                    'nodes': nodes_for_chunk
                })

            # Update file metadata store.
            self.metadata_store[file_path] = {
                'size': file_size,
                'chunks': new_chunks_metadata
            }
        return True

    def read_file(self, file_path: str) -> bytes:
        """
        Reads the entire content of the file at the given file path.
        Returns:
            The file's content as bytes, or None if the file was not found.
        """
        if not self._is_valid_path(file_path):
            return None

        with self.global_lock:
            if file_path not in self.metadata_store:
                return None
            # Obtain file lock for reading if a write might be in progress.
            file_lock = self.file_locks[file_path]

        with file_lock:
            metadata = self.metadata_store[file_path]
            total_chunks = len(metadata.get('chunks', []))
            if total_chunks == 0:
                return b""

            file_data = bytearray()
            # Read each chunk in order.
            for chunk_info in sorted(metadata['chunks'], key=lambda x: x['chunk_index']):
                chunk_id = self._get_chunk_identifier(file_path, chunk_info['chunk_index'])
                chunk_data = None
                # Try reading the chunk from any of its storage nodes.
                for node in chunk_info['nodes']:
                    if chunk_id in self.storage_nodes[node]:
                        chunk_data = self.storage_nodes[node][chunk_id]
                        break
                if chunk_data is None:
                    # If for some reason chunk_data is missing, return None indicating read failure.
                    return None
                file_data.extend(chunk_data)
            # Trim the output data in case the last chunk contains extra bytes.
            return bytes(file_data[:metadata['size']])

    def delete_file(self, file_path: str) -> bool:
        """
        Deletes the file at the given file path.
        Returns:
            True if the file was successfully deleted, False otherwise.
        """
        if not self._is_valid_path(file_path):
            return False

        with self.global_lock:
            if file_path not in self.metadata_store:
                return False
            # Retrieve file lock and metadata.
            file_lock = self.file_locks[file_path]

        with file_lock:
            metadata = self.metadata_store[file_path]
            for chunk_info in metadata.get('chunks', []):
                chunk_id = self._get_chunk_identifier(file_path, chunk_info['chunk_index'])
                for node in chunk_info['nodes']:
                    if chunk_id in self.storage_nodes[node]:
                        del self.storage_nodes[node][chunk_id]
            # Remove metadata and lock.
            with self.global_lock:
                del self.metadata_store[file_path]
                del self.file_locks[file_path]
        return True

    def _get_chunk_identifier(self, file_path: str, chunk_index: int) -> str:
        # Generate a unique identifier for a chunk using file path and chunk index.
        return f"{file_path}_{chunk_index}"