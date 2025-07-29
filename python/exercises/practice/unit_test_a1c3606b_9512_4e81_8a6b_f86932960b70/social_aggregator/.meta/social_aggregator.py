from collections import defaultdict, deque
import concurrent.futures
import time
import heapq
from typing import List, Dict, Any, Set, Tuple, Optional


def aggregate_and_rank_posts(user_ids: List[str], node_apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aggregates and ranks posts from a decentralized social network.
    
    Args:
        user_ids: List of user IDs to fetch posts for
        node_apis: List of node API dictionaries, each with get_posts_by_user and get_post methods
        
    Returns:
        List of post dictionaries, sorted according to the ranking criteria
    """
    if not user_ids or not node_apis:
        return []
    
    # Step 1: Create a distributed post fetcher to efficiently retrieve posts
    post_fetcher = DistributedPostFetcher(node_apis)
    
    # Step 2: Fetch all posts from the specified users
    author_post_counts = defaultdict(int)  # Track author popularity
    posts = []
    
    # Use ThreadPoolExecutor to fetch posts from users concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(32, len(user_ids))) as executor:
        future_to_user = {
            executor.submit(post_fetcher.get_posts_by_user, user_id): user_id
            for user_id in user_ids
        }
        
        for future in concurrent.futures.as_completed(future_to_user):
            user_id = future_to_user[future]
            try:
                user_posts = future.result()
                posts.extend(user_posts)
                author_post_counts[user_id] += len(user_posts)
            except Exception as e:
                # Log error but continue processing other users
                print(f"Error fetching posts for user {user_id}: {e}")
    
    if not posts:
        return []
    
    # Step 3: Build a post graph to resolve dependencies and calculate link depths
    post_graph = PostGraph(post_fetcher)
    
    # Add all posts to the graph
    for post in posts:
        post_graph.add_post(post)
    
    # Step 4: Calculate the link depth for each post
    link_depths = post_graph.calculate_link_depths()
    
    # Step 5: Calculate author popularity by counting posts across all nodes
    author_popularity = calculate_author_popularity(posts, post_fetcher, node_apis)
    
    # Step 6: Rank the posts based on the criteria
    ranked_posts = rank_posts(posts, link_depths, author_popularity)
    
    return ranked_posts


class DistributedPostFetcher:
    """Handles fetching posts from distributed nodes with fault tolerance."""
    
    def __init__(self, node_apis, timeout=5, max_retries=3):
        self.node_apis = node_apis
        self.timeout = timeout
        self.max_retries = max_retries
        self.post_cache = {}  # Cache to avoid redundant fetches
        self.failed_nodes = set()  # Track nodes that have failed
        
    def get_posts_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch posts by a user from all nodes."""
        all_posts = []
        
        # Try to fetch posts from each node
        for i, node_api in enumerate(self.node_apis):
            if i in self.failed_nodes:
                continue  # Skip nodes that have previously failed
                
            try:
                posts = self._fetch_with_retry(lambda: node_api["get_posts_by_user"](user_id))
                all_posts.extend(posts)
            except Exception as e:
                # Mark node as failed and continue with other nodes
                self.failed_nodes.add(i)
                print(f"Node {i} failed when fetching posts for user {user_id}: {e}")
        
        return all_posts
    
    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a post by ID from any node that has it."""
        # Check cache first
        if post_id in self.post_cache:
            return self.post_cache[post_id]
        
        # Try each node until we find the post
        for i, node_api in enumerate(self.node_apis):
            if i in self.failed_nodes:
                continue  # Skip nodes that have previously failed
                
            try:
                post = self._fetch_with_retry(lambda: node_api["get_post"](post_id))
                if post:
                    # Cache the post for future use
                    self.post_cache[post_id] = post
                    return post
            except Exception as e:
                # Mark node as failed and continue with other nodes
                self.failed_nodes.add(i)
                print(f"Node {i} failed when fetching post {post_id}: {e}")
        
        # Post not found or all nodes failed
        return None
    
    def _fetch_with_retry(self, fetch_fn):
        """Fetch with retry logic and timeout handling."""
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                # Use a simple timeout mechanism
                start_time = time.time()
                result = fetch_fn()
                if time.time() - start_time > self.timeout:
                    raise TimeoutError("Request timed out")
                return result
            except Exception as e:
                last_error = e
                retries += 1
                # Exponential backoff
                time.sleep(0.1 * (2 ** retries))
        
        # All retries failed
        raise last_error or Exception("Failed to fetch after multiple retries")


class PostGraph:
    """Manages the graph of posts and their links."""
    
    def __init__(self, post_fetcher, max_depth=10):
        self.post_fetcher = post_fetcher
        self.posts = {}  # Map of post_id to post dict
        self.outgoing_links = defaultdict(list)  # post_id -> list of post_ids it links to
        self.incoming_links = defaultdict(list)  # post_id -> list of post_ids that link to it
        self.max_depth = max_depth  # Maximum link depth to prevent excessive chain traversal
    
    def add_post(self, post: Dict[str, Any]):
        """Add a post to the graph."""
        post_id = post["post_id"]
        self.posts[post_id] = post
        
        # Add outgoing links
        for linked_post_id in post.get("links", []):
            self.outgoing_links[post_id].append(linked_post_id)
            self.incoming_links[linked_post_id].append(post_id)
            
            # Attempt to fetch the linked post if it's not already in the graph
            if linked_post_id not in self.posts:
                linked_post = self.post_fetcher.get_post(linked_post_id)
                if linked_post:
                    self.add_post(linked_post)
    
    def calculate_link_depths(self) -> Dict[str, int]:
        """Calculate the link depth for each post."""
        link_depths = {}
        
        # Process posts in topological order to handle dependencies efficiently
        for post_id in self.posts:
            if post_id not in link_depths:
                self._calculate_link_depth(post_id, link_depths, set())
        
        return link_depths
    
    def _calculate_link_depth(self, post_id: str, link_depths: Dict[str, int], visited: Set[str]) -> int:
        """Calculate link depth with cycle detection."""
        # Handle cycles
        if post_id in visited:
            return 0
        
        # Return cached depth if available
        if post_id in link_depths:
            return link_depths[post_id]
        
        # Base case: no outgoing links
        if post_id not in self.outgoing_links or not self.outgoing_links[post_id]:
            link_depths[post_id] = 0
            return 0
        
        # Prevent excessive recursion
        if len(visited) >= self.max_depth:
            link_depths[post_id] = len(visited)
            return len(visited)
        
        # Mark as visited for cycle detection
        visited.add(post_id)
        
        # Calculate maximum depth of outgoing links
        max_depth = 0
        for linked_post_id in self.outgoing_links[post_id]:
            # Skip if linked post doesn't exist
            if linked_post_id not in self.posts and not self.post_fetcher.get_post(linked_post_id):
                continue
                
            depth = self._calculate_link_depth(linked_post_id, link_depths, visited.copy())
            max_depth = max(max_depth, depth + 1)
        
        # Store and return result
        link_depths[post_id] = max_depth
        return max_depth


def calculate_author_popularity(posts: List[Dict[str, Any]], post_fetcher: DistributedPostFetcher, node_apis: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate author popularity (total post count) for all authors."""
    # Start with the authors from our current posts
    authors = set(post["author_id"] for post in posts)
    popularity = defaultdict(int)
    
    # Count posts for each author across all nodes
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(32, len(authors))) as executor:
        future_to_author = {
            executor.submit(post_fetcher.get_posts_by_user, author): author
            for author in authors
        }
        
        for future in concurrent.futures.as_completed(future_to_author):
            author = future_to_author[future]
            try:
                author_posts = future.result()
                popularity[author] += len(author_posts)
            except Exception as e:
                # Log error but continue with default count
                print(f"Error counting posts for author {author}: {e}")
                # Use what we already know about this author from our posts
                popularity[author] = sum(1 for post in posts if post["author_id"] == author)
    
    return popularity


def rank_posts(posts: List[Dict[str, Any]], link_depths: Dict[str, int], author_popularity: Dict[str, int]) -> List[Dict[str, Any]]:
    """Rank posts based on timestamp, link depth, and author popularity."""
    # Create a ranking score for each post
    ranked_posts = []
    for post in posts:
        post_id = post["post_id"]
        # Use negative values for sorting in reverse order (highest first)
        timestamp = -post.get("timestamp", 0)
        link_depth = -link_depths.get(post_id, 0)
        popularity = -author_popularity.get(post["author_id"], 0)
        
        # Create tuple for sorting (timestamp, link_depth, author_popularity, post_id for consistency)
        ranking = (timestamp, link_depth, popularity, post_id)
        ranked_posts.append((ranking, post))
    
    # Sort posts based on ranking
    ranked_posts.sort()
    
    # Return just the post dictionaries in ranked order
    return [post for _, post in ranked_posts]