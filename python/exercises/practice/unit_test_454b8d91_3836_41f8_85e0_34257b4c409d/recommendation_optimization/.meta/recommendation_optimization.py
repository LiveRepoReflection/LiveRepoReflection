import time
from concurrent.futures import ThreadPoolExecutor

class RecommendationEngine:
    def __init__(self, user_profile_service, product_catalog_service, order_history_service, inventory_service, cache_enabled=True, cache_ttl=300):
        self.user_profile_service = user_profile_service
        self.product_catalog_service = product_catalog_service
        self.order_history_service = order_history_service
        self.inventory_service = inventory_service
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self.cache = {}

    def get_recommendations(self, user_id):
        # Check if cached value exists and is valid
        if self.cache_enabled:
            cached = self.cache.get(user_id)
            if cached:
                timestamp, recommendations = cached
                if time.time() - timestamp < self.cache_ttl:
                    return recommendations

        # Use ThreadPoolExecutor to fetch data concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_profile = executor.submit(self.user_profile_service.get_user_profile, user_id)
            future_products = executor.submit(self.product_catalog_service.get_products)
            future_orders = executor.submit(self.fetch_order_history, user_id)
            try:
                profile = future_profile.result()
            except Exception:
                profile = {}
            try:
                products = future_products.result()
            except Exception:
                products = []
            try:
                orders = future_orders.result()
            except Exception:
                orders = []

        preferences = profile.get("preferences", []) if profile else []

        def process_product(product):
            score = 0
            if product.get("category") in preferences:
                score += 10
            score += product.get("popularity", 0) / 10
            if orders:
                for order in orders:
                    if product.get("product_id") in order.get("items", []):
                        score += 5
            try:
                inv = self.inventory_service.get_inventory(product.get("product_id"))
                if inv.get("stock", 0) <= 0:
                    score = -1
            except Exception:
                score = 0
            if score > 0:
                return (score, product)
            return None

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(process_product, products))

        filtered_products = [res for res in results if res is not None]
        filtered_products.sort(key=lambda x: x[0], reverse=True)
        recommendations = [prod.get("product_id") for score, prod in filtered_products]

        if self.cache_enabled:
            self.cache[user_id] = (time.time(), recommendations)
        return recommendations

    def fetch_order_history(self, user_id):
        return self.order_history_service.get_order_history(user_id)