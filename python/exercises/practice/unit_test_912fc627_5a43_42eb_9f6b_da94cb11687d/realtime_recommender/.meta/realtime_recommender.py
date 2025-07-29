import numpy as np
import time
import heapq
from collections import defaultdict, Counter
from typing import Dict, List, Union, Set, Tuple, Any, Optional

class RealtimeRecommender:
    def __init__(self):
        # Product catalog: product_id -> product features
        self.products: Dict[int, Dict[str, Any]] = {}
        
        # User-item interaction history: user_id -> [(product_id, event_type, timestamp), ...]
        self.user_interactions: Dict[int, List[Tuple[int, str, int]]] = defaultdict(list)
        
        # Similarity matrix for products: product_id -> {product_id -> similarity_score}
        self.product_similarities: Dict[int, Dict[int, float]] = {}
        
        # Event type weights
        self.event_weights = {
            "view": 1.0,
            "cart": 2.0,
            "purchase": 3.0
        }
        
        # Time decay parameters
        self.time_decay_factor = 0.5  # Half-life in days
        self.time_decay_base = 2.0
        
        # Balance between user-item affinity and product similarity
        self.user_weight = 0.7
        self.similarity_weight = 0.3

    def add_product(self, product: Dict[str, Any]) -> None:
        """
        Add a product to the catalog and precompute similarities.
        
        Args:
            product: A dictionary containing product_id and features
        """
        product_id = product.get("product_id")
        features = product.get("features", [])
        
        if not isinstance(product_id, int) or not isinstance(features, list):
            raise ValueError("Invalid product format")
        
        if product_id <= 0:
            raise ValueError("product_id must be positive")
        
        # Store product
        self.products[product_id] = {
            "product_id": product_id,
            "features": features,
            "norm": np.linalg.norm(features) if features else 1.0
        }
        
        # Precompute similarities with existing products
        if product_id not in self.product_similarities:
            self.product_similarities[product_id] = {}
            
        for pid, p in self.products.items():
            if pid != product_id:
                # Calculate similarity using cosine similarity
                similarity = self._calculate_similarity(product_id, pid)
                self.product_similarities[product_id][pid] = similarity
                
                # Update the similarity in the other direction too
                if pid not in self.product_similarities:
                    self.product_similarities[pid] = {}
                self.product_similarities[pid][product_id] = similarity

    def add_interaction(self, event: Dict[str, Any]) -> None:
        """
        Add a user-product interaction event.
        
        Args:
            event: A dictionary containing user_id, product_id, event_type, and timestamp
        """
        user_id = event.get("user_id")
        product_id = event.get("product_id")
        event_type = event.get("event_type")
        timestamp = event.get("timestamp")
        
        if not all(isinstance(v, (int, str)) for v in [user_id, product_id, event_type, timestamp]):
            raise ValueError("Invalid event format")
            
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("user_id must be a positive integer")
            
        if not isinstance(product_id, int) or product_id <= 0:
            raise ValueError("product_id must be a positive integer")
            
        if event_type not in self.event_weights:
            raise ValueError(f"event_type must be one of {list(self.event_weights.keys())}")
            
        if not isinstance(timestamp, int):
            raise ValueError("timestamp must be an integer")
        
        # Check if product exists
        if product_id not in self.products:
            raise ValueError(f"Product {product_id} does not exist in the catalog")
        
        # Add to user interactions
        self.user_interactions[user_id].append((product_id, event_type, timestamp))
    
    def get_recommendations(self, user_id: int, product_id: int, k: int) -> List[int]:
        """
        Get k recommendations for a user viewing a product.
        
        Args:
            user_id: The user ID
            product_id: The product ID being viewed
            k: The number of recommendations to return
            
        Returns:
            A list of recommended product IDs
        """
        # Validate inputs
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("user_id must be a positive integer")
            
        if not isinstance(product_id, int) or product_id <= 0:
            raise ValueError("product_id must be a positive integer")
            
        if not isinstance(k, int) or k <= 0 or k > 100:
            raise ValueError("k must be an integer between 1 and 100")
        
        # Check if product exists
        if product_id not in self.products:
            raise ValueError(f"Product {product_id} does not exist in the catalog")
        
        # Get all candidate products (all products except the one being viewed)
        candidate_products = set(self.products.keys()) - {product_id}
        
        # Calculate scores for each candidate product
        product_scores = {}
        
        for candidate_pid in candidate_products:
            # Calculate product similarity score
            similarity_score = self.product_similarities[product_id].get(candidate_pid, 0.0)
            
            # Calculate user-item affinity score
            user_affinity_score = self._calculate_user_affinity(user_id, candidate_pid)
            
            # Combine scores
            combined_score = (self.user_weight * user_affinity_score + 
                              self.similarity_weight * similarity_score)
            
            product_scores[candidate_pid] = combined_score
        
        # Get top k products with highest scores
        top_k_products = heapq.nlargest(k, product_scores.items(), key=lambda x: x[1])
        top_k_product_ids = [pid for pid, score in top_k_products]
        
        return top_k_product_ids
    
    def _calculate_similarity(self, product1_id: int, product2_id: int) -> float:
        """
        Calculate the similarity between two products using cosine similarity.
        
        Args:
            product1_id: The first product ID
            product2_id: The second product ID
            
        Returns:
            The similarity score between 0 and 1
        """
        product1 = self.products[product1_id]
        product2 = self.products[product2_id]
        
        features1 = product1["features"]
        features2 = product2["features"]
        
        if not features1 or not features2:
            return 0.0
        
        # Calculate cosine similarity
        dot_product = np.dot(features1, features2)
        norm1 = product1["norm"]
        norm2 = product2["norm"]
        
        if norm1 * norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    
    def _calculate_user_affinity(self, user_id: int, product_id: int) -> float:
        """
        Calculate the affinity between a user and a product based on interaction history.
        
        Args:
            user_id: The user ID
            product_id: The product ID
            
        Returns:
            The user-item affinity score
        """
        # If user has no interactions, return 0
        if user_id not in self.user_interactions:
            return 0.0
        
        user_interactions = self.user_interactions[user_id]
        current_time = int(time.time())
        
        # Calculate the weighted sum of interactions with this product
        affinity_score = 0.0
        
        for pid, event_type, timestamp in user_interactions:
            # Apply time decay
            days_passed = (current_time - timestamp) / (24 * 3600)
            time_decay = self.time_decay_base ** (-days_passed / self.time_decay_factor)
            
            # Apply event weight
            event_weight = self.event_weights.get(event_type, 1.0)
            
            # Direct interaction with this product
            if pid == product_id:
                affinity_score += event_weight * time_decay
            else:
                # Indirect interaction through product similarity
                similarity = self.product_similarities.get(pid, {}).get(product_id, 0.0)
                affinity_score += event_weight * time_decay * similarity * 0.5  # Indirect interactions have half the weight
        
        return affinity_score

def get_recommendations(user_id: int, product_id: int, k: int) -> List[int]:
    """
    Wrapper function for the RealtimeRecommender.get_recommendations method.
    In a real-world scenario, this would use a singleton instance.
    
    Args:
        user_id: The user ID
        product_id: The product ID being viewed
        k: The number of recommendations to return
        
    Returns:
        A list of recommended product IDs
    """
    # In a real application, this would be a singleton instance
    recommender = RealtimeRecommender()
    
    # Here we would load products and interactions from a database
    # but for this example, we'll use an empty recommender
    
    return recommender.get_recommendations(user_id, product_id, k)