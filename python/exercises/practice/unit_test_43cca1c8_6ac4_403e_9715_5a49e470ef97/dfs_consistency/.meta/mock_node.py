import random

class MockNode:
    """
    Mock storage node implementation for testing purposes.
    """
    def __init__(self, node_id):
        self.node_id = node_id
        self.chunks = {}
        
    def add_chunk(self, chunk_id, version, size):
        self.chunks[chunk_id] = {
            'chunk_id': chunk_id,
            'version': version,
            'size': size
        }
        
    def get_chunk_metadata(self):
        return list(self.chunks.values())

def setup_mock_nodes():
    """
    Helper function to set up mock nodes with test data.
    Returns a dictionary of {node_address: MockNode}
    """
    nodes = {
        'node1': MockNode('node1'),
        'node2': MockNode('node2'),
        'node3': MockNode('node3')
    }
    
    # Add consistent chunks
    nodes['node1'].add_chunk('chunk1', 1, 1024)
    nodes['node2'].add_chunk('chunk1', 1, 1024)
    nodes['node3'].add_chunk('chunk1', 1, 1024)
    
    # Add inconsistent chunks
    nodes['node1'].add_chunk('chunk2', 1, 2048)
    nodes['node2'].add_chunk('chunk2', 2, 2048)  # Version mismatch
    nodes['node3'].add_chunk('chunk2', 1, 2048)
    
    nodes['node1'].add_chunk('chunk3', 1, 1024)
    nodes['node2'].add_chunk('chunk3', 1, 2048)  # Size mismatch
    nodes['node3'].add_chunk('chunk3', 1, 1024)
    
    return nodes