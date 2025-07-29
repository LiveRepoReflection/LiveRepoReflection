import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Set
from collections import defaultdict

@dataclass
class Warehouse:
    id: str
    location: Tuple[float, float]  # (latitude, longitude)
    inventory: Dict[str, int]  # product_id: quantity

@dataclass
class Store:
    id: str
    location: Tuple[float, float]  # (latitude, longitude)
    demand: Dict[str, int]  # product_id: quantity
    unfulfilled_penalty: Dict[str, float]  # product_id: penalty per unit

def haversine_distance(loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
    """Calculate the great-circle distance between two points on Earth."""
    lat1, lon1 = math.radians(loc1[0]), math.radians(loc1[1])
    lat2, lon2 = math.radians(loc2[0]), math.radians(loc2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth radius in kilometers
    r = 6371
    return c * r

def optimize_supply_chain(
    warehouses: List[Warehouse],
    stores: List[Store],
    transportation_rate: float
) -> Dict[Tuple[str, str, str], int]:
    """Optimize the supply chain to minimize total cost.
    
    Returns:
        A dictionary where keys are (warehouse_id, store_id, product_id) tuples
        and values are quantities to ship.
    """
    if not warehouses or not stores or transportation_rate < 0:
        raise ValueError("Invalid input parameters")
    
    # Precompute distances between all warehouses and stores
    distance_cache = {}
    for wh in warehouses:
        for store in stores:
            distance_cache[(wh.id, store.id)] = haversine_distance(wh.location, store.location)
    
    # Initialize shipping plan
    shipping_plan = defaultdict(int)
    
    # Track remaining inventory and demand
    remaining_inventory = {wh.id: wh.inventory.copy() for wh in warehouses}
    remaining_demand = {store.id: store.demand.copy() for store in stores}
    
    # Process each product separately
    all_products = set()
    for wh in warehouses:
        all_products.update(wh.inventory.keys())
    for store in stores:
        all_products.update(store.demand.keys())
    
    for product in all_products:
        # Create list of all possible shipments for this product
        shipments = []
        
        for wh in warehouses:
            if product not in remaining_inventory[wh.id] or remaining_inventory[wh.id][product] <= 0:
                continue
                
            for store in stores:
                if product not in remaining_demand[store.id] or remaining_demand[store.id][product] <= 0:
                    continue
                
                distance = distance_cache[(wh.id, store.id)]
                cost_per_unit = distance * transportation_rate
                penalty = store.unfulfilled_penalty.get(product, float('inf'))
                
                # Calculate maximum possible quantity to ship
                max_qty = min(
                    remaining_inventory[wh.id][product],
                    remaining_demand[store.id][product]
                )
                
                if max_qty > 0:
                    shipments.append((
                        cost_per_unit,
                        penalty,
                        wh.id,
                        store.id,
                        product,
                        max_qty
                    ))
        
        # Sort shipments by cost effectiveness
        shipments.sort(key=lambda x: (x[0], x[1]))
        
        # Process shipments in order of cost effectiveness
        for cost, penalty, wh_id, store_id, prod_id, max_qty in shipments:
            if remaining_demand[store_id][prod_id] <= 0:
                continue
                
            # Calculate how much to ship
            qty = min(
                remaining_inventory[wh_id][prod_id],
                remaining_demand[store_id][prod_id]
            )
            
            if qty > 0:
                shipping_plan[(wh_id, store_id, prod_id)] += qty
                remaining_inventory[wh_id][prod_id] -= qty
                remaining_demand[store_id][prod_id] -= qty
    
    return dict(shipping_plan)