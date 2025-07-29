import threading
from collections import defaultdict
from bisect import bisect_left, insort

class OnlineMarketplace:
    def __init__(self):
        self.lock = threading.Lock()
        self.assets = {}  # {asset_id: (price, attributes)}
        self.price_index = []  # Sorted list of (price, asset_id)
        self.id_index = []  # Sorted list of asset_ids
        self.attribute_index = defaultdict(dict)  # {attr: {value: set(asset_ids)}}

    def add_asset(self, asset_id, price, attributes):
        with self.lock:
            if asset_id in self.assets:
                raise ValueError(f"Asset {asset_id} already exists")
            
            self.assets[asset_id] = (price, attributes)
            insort(self.price_index, (price, asset_id))
            insort(self.id_index, asset_id)
            
            for attr in attributes:
                key, value = attr.split(':', 1)
                if value not in self.attribute_index[key]:
                    self.attribute_index[key][value] = set()
                self.attribute_index[key][value].add(asset_id)

    def update_price(self, asset_id, new_price):
        with self.lock:
            if asset_id not in self.assets:
                raise ValueError(f"Asset {asset_id} not found")
                
            old_price, attributes = self.assets[asset_id]
            if old_price == new_price:
                return
                
            # Remove from price index
            pos = bisect_left(self.price_index, (old_price, asset_id))
            if pos != len(self.price_index) and self.price_index[pos] == (old_price, asset_id):
                self.price_index.pop(pos)
                
            # Update price and reinsert
            self.assets[asset_id] = (new_price, attributes)
            insort(self.price_index, (new_price, asset_id))

    def remove_asset(self, asset_id):
        with self.lock:
            if asset_id not in self.assets:
                raise ValueError(f"Asset {asset_id} not found")
                
            price, attributes = self.assets.pop(asset_id)
            
            # Remove from price index
            pos = bisect_left(self.price_index, (price, asset_id))
            if pos != len(self.price_index) and self.price_index[pos] == (price, asset_id):
                self.price_index.pop(pos)
                
            # Remove from id index
            pos = bisect_left(self.id_index, asset_id)
            if pos != len(self.id_index) and self.id_index[pos] == asset_id:
                self.id_index.pop(pos)
                
            # Remove from attribute index
            for attr in attributes:
                key, value = attr.split(':', 1)
                if key in self.attribute_index and value in self.attribute_index[key]:
                    self.attribute_index[key][value].discard(asset_id)
                    if not self.attribute_index[key][value]:
                        del self.attribute_index[key][value]

    def search(self, query, sort_by, limit):
        with self.lock:
            # Parse query
            filters = []
            if query:
                for condition in query.split(' AND '):
                    if ':' not in condition:
                        continue
                    key, value = condition.split(':', 1)
                    filters.append((key.strip(), value.strip()))
            
            # Find matching assets
            if not filters:
                matching_ids = set(self.assets.keys())
            else:
                matching_ids = None
                for key, value in filters:
                    if key in self.attribute_index and value in self.attribute_index[key]:
                        ids = self.attribute_index[key][value]
                        matching_ids = ids if matching_ids is None else matching_ids & ids
                    else:
                        matching_ids = set()
                        break
            
            if not matching_ids:
                return []
            
            # Prepare results
            results = []
            for asset_id in matching_ids:
                price, _ = self.assets[asset_id]
                results.append((asset_id, price))
            
            # Sort results
            if sort_by == "price":
                results.sort(key=lambda x: (x[1], x[0]))
            elif sort_by == "asset_id":
                results.sort(key=lambda x: x[0])
            else:
                raise ValueError("Invalid sort_by parameter")
            
            # Apply limit
            return results[:limit]

    def bulk_load(self, assets):
        with self.lock:
            # Temporary storage for bulk operations
            new_assets = {}
            new_price_index = []
            new_id_index = []
            new_attribute_index = defaultdict(dict)
            
            for asset_id, price, attributes in assets:
                if asset_id in self.assets or asset_id in new_assets:
                    continue
                    
                new_assets[asset_id] = (price, attributes)
                insort(new_price_index, (price, asset_id))
                insort(new_id_index, asset_id)
                
                for attr in attributes:
                    key, value = attr.split(':', 1)
                    if value not in new_attribute_index[key]:
                        new_attribute_index[key][value] = set()
                    new_attribute_index[key][value].add(asset_id)
            
            # Merge with existing data
            self.assets.update(new_assets)
            
            # Merge price index (using efficient merge of sorted lists)
            merged_price = []
            i = j = 0
            while i < len(self.price_index) and j < len(new_price_index):
                if self.price_index[i] < new_price_index[j]:
                    merged_price.append(self.price_index[i])
                    i += 1
                else:
                    merged_price.append(new_price_index[j])
                    j += 1
            merged_price.extend(self.price_index[i:])
            merged_price.extend(new_price_index[j:])
            self.price_index = merged_price
            
            # Merge id index
            merged_ids = []
            i = j = 0
            while i < len(self.id_index) and j < len(new_id_index):
                if self.id_index[i] < new_id_index[j]:
                    merged_ids.append(self.id_index[i])
                    i += 1
                else:
                    merged_ids.append(new_id_index[j])
                    j += 1
            merged_ids.extend(self.id_index[i:])
            merged_ids.extend(new_id_index[j:])
            self.id_index = merged_ids
            
            # Merge attribute index
            for key, values in new_attribute_index.items():
                if key not in self.attribute_index:
                    self.attribute_index[key] = {}
                for value, ids in values.items():
                    if value not in self.attribute_index[key]:
                        self.attribute_index[key][value] = set()
                    self.attribute_index[key][value].update(ids)