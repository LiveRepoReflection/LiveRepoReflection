import hashlib
from typing import List, Tuple, Dict, Set
import heapq

# Global in-memory data store
# Structure: {user_id: [(timestamp, content, cid)]}
_user_posts: Dict[str, List[Tuple[int, str, str]]] = {}

# Secondary index mapping CIDs to posts
# Structure: {cid: (user_id, timestamp, content)}
_cid_index: Dict[str, Tuple[str, int, str]] = {}

# Node to content mapping (simulating DHT storage)
# Structure: {node_id: {cid: (user_id, timestamp, content)}}
_node_storage: Dict[int, Dict[str, Tuple[str, int, str]]] = {}

# Default replication factor
DEFAULT_K = 5
# Total number of nodes in the network
NETWORK_SIZE = 100000
# Maximum node ID
MAX_NODE_ID = 2**20 - 1

def calculate_cid(user_id: str, timestamp: int, content: str) -> str:
    """Calculate the Content ID (CID) for a post using SHA-256."""
    data = f"{user_id}:{timestamp}:{content}".encode()
    return hashlib.sha256(data).hexdigest()

def xor_distance(id1: int, id2: int) -> int:
    """Calculate the XOR distance between two node IDs."""
    return id1 ^ id2

def get_closest_nodes(target_id: int, k: int = DEFAULT_K) -> List[int]:
    """Get the k closest nodes to a target ID using XOR distance."""
    # Convert target_id from hex to int if it's a string (CID)
    if isinstance(target_id, str):
        # Take first 16 characters of CID to fit within node ID range
        target_int = int(target_id[:16], 16) % (MAX_NODE_ID + 1)
    else:
        target_int = target_id
    
    # Calculate distances for all nodes (simplified approach)
    # In a real implementation, this would use DHT routing instead of checking all nodes
    distances = []
    for node_id in range(0, MAX_NODE_ID + 1, MAX_NODE_ID // 1000):  # Sample nodes for efficiency
        if node_id not in _node_storage:
            _node_storage[node_id] = {}
        distance = xor_distance(node_id, target_int)
        heapq.heappush(distances, (distance, node_id))
    
    # Return the k closest nodes
    return [node_id for _, node_id in heapq.nsmallest(k, distances)]

def store_post(node_id: int, user_id: str, timestamp: int, content: str, k: int = DEFAULT_K) -> str:
    """Store a post in the DHT and return its CID."""
    # Calculate the Content ID
    cid = calculate_cid(user_id, timestamp, content)
    
    # Store in user posts index
    if user_id not in _user_posts:
        _user_posts[user_id] = []
    _user_posts[user_id].append((timestamp, content, cid))
    
    # Store in CID index
    _cid_index[cid] = (user_id, timestamp, content)
    
    # Find k closest nodes to the CID
    closest_nodes = get_closest_nodes(cid, k)
    
    # Store the post on each of the k closest nodes
    for node in closest_nodes:
        if node not in _node_storage:
            _node_storage[node] = {}
        _node_storage[node][cid] = (user_id, timestamp, content)
    
    return cid

def retrieve_posts(node_id: int, user_id: str) -> List[Tuple[int, str]]:
    """Retrieve all posts by a user, sorted by timestamp in descending order."""
    # Check if we have the user's posts in our in-memory index
    # This is a simplified approach; in a real DHT, we'd need to query nodes
    if user_id in _user_posts:
        # Sort posts by timestamp in descending order
        sorted_posts = sorted(_user_posts[user_id], key=lambda x: x[0], reverse=True)
        # Return (timestamp, content) pairs
        return [(ts, content) for ts, content, _ in sorted_posts]
    
    # If we don't have the user's posts in our index, we need to search the network
    # This is where we would query the DHT in a real implementation
    # For this exercise, we'll simulate by checking all nodes (inefficient but demonstrates the concept)
    
    # First, create a bloom filter for the user_id to optimize node selection
    # (In a real system, you might use a distributed index for this)
    user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % (MAX_NODE_ID + 1)
    potential_nodes = get_closest_nodes(user_hash, DEFAULT_K * 5)  # Query more nodes for better coverage
    
    # Search for posts on the potential nodes
    posts = []
    seen_cids = set()
    
    for node in potential_nodes:
        if node in _node_storage:
            for cid, (post_user_id, timestamp, content) in _node_storage[node].items():
                if post_user_id == user_id and cid not in seen_cids:
                    posts.append((timestamp, content))
                    seen_cids.add(cid)
    
    # Sort posts by timestamp in descending order
    return sorted(posts, key=lambda x: x[0], reverse=True)