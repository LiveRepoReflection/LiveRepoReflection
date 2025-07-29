import time
import threading

class RecommendationSystem:
    def __init__(self):
        self.catalog = {}  # product_id -> product info
        self.user_profiles = {}  # user_id -> profile info
        self.events = []  # list of events
        self.current_algorithm = "collaborative_filtering"
        self.metrics = {
            'hit_rate': 0.0,
            'click_through_rate': 0.0,
            'latency': 0.0
        }
        self.lock = threading.Lock()

    def update_catalog(self, product):
        """
        Update or add product in the catalog.
        Expected product format: {
            'product_id': int,
            'category': str,
            'price': float,
            'other_features': dict
        }
        """
        if 'product_id' not in product or 'category' not in product or 'price' not in product or 'other_features' not in product:
            raise Exception("Malformed product data")
        with self.lock:
            self.catalog[product['product_id']] = product

    def update_user_profile(self, profile):
        """
        Update or add user profile.
        Expected profile format: {
            'user_id': int,
            'purchase_history': list of product_id,
            'view_history': list of product_id,
            'other_features': dict
        }
        """
        if 'user_id' not in profile or 'purchase_history' not in profile or 'view_history' not in profile or 'other_features' not in profile:
            raise Exception("Malformed user profile data")
        with self.lock:
            self.user_profiles[profile['user_id']] = profile

    def update_event(self, event):
        """
        Process an event.
        Expected event format: {
            'user_id': int,
            'event_type': str (must be one of "view", "purchase", "add_to_cart"),
            'product_id': int,
            'timestamp': int
        }
        """
        if ('user_id' not in event or 'event_type' not in event or
            'product_id' not in event or 'timestamp' not in event):
            raise Exception("Malformed event data")
        if event['event_type'] not in {"view", "purchase", "add_to_cart"}:
            raise Exception("Invalid event type")
        with self.lock:
            self.events.append(event)
            # Update user profile if exists, otherwise create a new one (cold start)
            user_id = event['user_id']
            if user_id not in self.user_profiles:
                # Initialize a cold-start user with empty histories
                self.user_profiles[user_id] = {
                    'user_id': user_id,
                    'purchase_history': [],
                    'view_history': [],
                    'other_features': {}
                }
            # Update histories based on event type
            if event['event_type'] == "purchase":
                self.user_profiles[user_id]['purchase_history'].append(event['product_id'])
            elif event['event_type'] == "view":
                self.user_profiles[user_id]['view_history'].append(event['product_id'])
            # For add_to_cart, we don't change histories for this simple implementation

    def get_recommendations(self, user_id, k):
        """
        Return a list of recommended product_ids for the user.
        The recommendation algorithm is selected based on self.current_algorithm.
        """
        start_time = time.time()
        with self.lock:
            # If user not found, treat as cold start and return the first k products (sorted by product_id)
            if user_id not in self.user_profiles:
                recs = sorted(self.catalog.keys())[:k]
                self.metrics['latency'] = (time.time() - start_time) * 1000
                return recs

            user_profile = self.user_profiles[user_id]
            if self.current_algorithm == "collaborative_filtering":
                recommendations = self._collaborative_filtering(user_profile, k)
            elif self.current_algorithm == "content_based":
                recommendations = self._content_based(user_profile, k)
            else:
                # Default to collaborative filtering if algorithm is unknown
                recommendations = self._collaborative_filtering(user_profile, k)
        self.metrics['latency'] = (time.time() - start_time) * 1000
        return recommendations

    def switch_algorithm(self, algorithm):
        """
        Switch the current recommendation algorithm.
        Supported algorithms: "collaborative_filtering", "content_based"
        """
        if algorithm not in {"collaborative_filtering", "content_based"}:
            raise Exception("Unsupported algorithm")
        with self.lock:
            self.current_algorithm = algorithm

    def report_metrics(self):
        """
        Return performance metrics of the system.
        """
        with self.lock:
            # For demonstration, metrics are gathered, though they are dummy calculations.
            return {
                'hit_rate': self.metrics['hit_rate'],
                'click_through_rate': self.metrics['click_through_rate'],
                'latency': self.metrics['latency']
            }

    def _collaborative_filtering(self, user_profile, k):
        """
        A stub implementation of collaborative filtering.
        Recommend products based on the behavior of similar users (aggregated from purchase and view history).
        In this simplified version, the recommendation score is computed by frequency of occurrence 
        in the combined history across all users (excluding the user's own history).
        """
        score = {}
        # Accumulate scores from other users
        for uid, profile in self.user_profiles.items():
            if uid == user_profile['user_id']:
                continue
            for pid in profile.get('purchase_history', []) + profile.get('view_history', []):
                if pid in self.catalog:
                    score[pid] = score.get(pid, 0) + 1
        # Exclude products the user has already seen or purchased
        seen = set(user_profile.get('purchase_history', []) + user_profile.get('view_history', []))
        candidate_scores = [(pid, s) for pid, s in score.items() if pid not in seen]
        # If not enough products, include unseen ones from catalog
        if len(candidate_scores) < k:
            additional = []
            for pid in self.catalog:
                if pid not in seen and pid not in [x[0] for x in candidate_scores]:
                    additional.append((pid, 0))
            candidate_scores.extend(additional)
        # Sort recommendations by score descending then by product_id
        candidate_scores.sort(key=lambda x: (-x[1], x[0]))
        recommendations = [pid for pid, _ in candidate_scores][:k]
        # If still fewer than k recommendations, pad with any available products
        if len(recommendations) < k:
            all_products = list(self.catalog.keys())
            for pid in all_products:
                if pid not in recommendations:
                    recommendations.append(pid)
                if len(recommendations) == k:
                    break
        return recommendations

    def _content_based(self, user_profile, k):
        """
        A stub implementation of content-based filtering.
        Recommend products based on the similarity of categories in the user's purchase history.
        """
        preferred_categories = {}
        # Count frequency of categories in purchase history
        for pid in user_profile.get('purchase_history', []):
            product = self.catalog.get(pid)
            if product:
                cat = product['category']
                preferred_categories[cat] = preferred_categories.get(cat, 0) + 1
        # Compute recommendation scores for each product in catalog that user hasn't already interacted with
        seen = set(user_profile.get('purchase_history', []) + user_profile.get('view_history', []))
        scores = []
        for pid, product in self.catalog.items():
            if pid in seen:
                continue
            score = preferred_categories.get(product['category'], 0)
            scores.append((pid, score))
        # If not enough recommendations, add products with zero score if necessary.
        if len(scores) < k:
            for pid, product in self.catalog.items():
                if pid not in seen and all(pid != s[0] for s in scores):
                    scores.append((pid, 0))
        scores.sort(key=lambda x: (-x[1], x[0]))
        recommendations = [pid for pid, _ in scores][:k]
        # If still not enough, pad with arbitrary products
        if len(recommendations) < k:
            for pid in self.catalog:
                if pid not in recommendations:
                    recommendations.append(pid)
                if len(recommendations) == k:
                    break
        return recommendations