"""
Example script demonstrating how to use the distributed file system.
This would not typically be included in a package but serves as a usage example.
"""
from io import BytesIO
from dist_file_sys import StorageNode, MetadataServer, DistributedFileSystem

def main():
    # Create storage nodes
    num_nodes = 5
    storage_nodes = [StorageNode(i) for i in range(num_nodes)]
    
    # Create metadata server
    metadata_server = MetadataServer()
    
    # Create distributed file system with a replication factor of 3
    # and a smaller chunk size for demonstration purposes (1MB)
    dfs = DistributedFileSystem(
        storage_nodes,
        metadata_server,
        replication_factor=3,
        chunk_size=1024 * 1024  # 1MB
    )
    
    # Write a file
    file_path = "/example/hello.txt"
    content = b"Hello, distributed world! " * 10000  # Make it bigger than a chunk
    print(f"Writing file {file_path} with size {len(content)} bytes")
    dfs.write(file_path, BytesIO(content))
    print("Write successful")
    
    # Read the file back
    print(f"Reading file {file_path}")
    result = dfs.read(file_path)
    retrieved_content = result.read()
    
    # Verify the content matches
    print(f"Read {len(retrieved_content)} bytes")
    print("Content matches: ", retrieved_content == content)
    
    # Try reading a non-existent file
    try:
        print("Trying to read a non-existent file")
        dfs.read("/nonexistent/file.txt")
    except Exception as e:
        print(f"Expected error: {e}")
    
    print("Example completed successfully")

if __name__ == "__main__":
    main()