from typing import Dict
from random import random
from time import sleep

class OrderService:
    def __init__(self):
        self.orders = {}
        self.next_order_id = 1

    def prepare(self, data: Dict) -> bool:
        sleep(0.1 * random())
        if random() < 0.05:  # 5% chance of failure
            return False
        return True

    def commit(self, data: Dict) -> bool:
        sleep(0.1 * random())
        if random() < 0.05:  # 5% chance of failure
            return False
        self.orders[self.next_order_id] = data
        self.next_order_id += 1
        return True

    def rollback(self, data: Dict) -> bool:
        sleep(0.1 * random())
        return True

class InventoryService:
    def __init__(self):
        self.inventory = {'1': 100, '2': 50, '3': 200}  # item_id: quantity

    def prepare(self, data: Dict) -> bool:
        sleep(0.1 * random())
        if random() < 0.05:
            return False
            
        for item in data['items']:
            if str(item['id']) not in self.inventory or \
               self.inventory[str(item['id'])] < item['quantity']:
                return False
        return True

    def commit(self, data: Dict) -> bool:
        sleep(0.1 * random())
        if random() < 0.05:
            return False
            
        for item in data['items']:
            self.inventory[str(item['id'])] -= item['quantity']
        return True

    def rollback(self, data: Dict) -> bool:
        sleep(0.1 * random())
        return True

class PaymentService:
    def __init__(self):
        self.transactions = {}

    def prepare(self, data: Dict) -> bool:
        sleep(0.1 * random())
        if random() < 0.05:
            return False
        return data['payment']['amount'] > 0

    def commit(self, data: Dict) -> bool:
        sleep(0.1 * random())
        if random() < 0.05:
            return False
        self.transactions[len(self.transactions)+1] = data['payment']
        return True

    def rollback(self, data: Dict) -> bool:
        sleep(0.1 * random())
        return True

class ShippingService:
    def __init__(self):
        self.shipments = []

    def prepare(self, data: Dict) -> bool:
        sleep(0.1 * random())
        if random() < 0.05:
            return False
        return True

    def commit(self, data: Dict) -> bool:
        sleep(0.1 * random())
        if random() < 0.05:
            return False
        self.shipments.append({
            'order_data': data,
            'status': 'pending'
        })
        return True

    def rollback(self, data: Dict) -> bool:
        sleep(0.1 * random())
        return True