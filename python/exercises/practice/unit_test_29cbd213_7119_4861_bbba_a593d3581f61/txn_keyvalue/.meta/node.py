import threading
import time
from collections import defaultdict

class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.lock = threading.Lock()
        self.data = {}  # Current committed data
        self.versions = defaultdict(dict)  # Version store for MVCC
        self.transactions = {}  # Active transactions
        self.version_counter = 0
        self.active_transactions = set()
    
    def start_transaction(self):
        with self.lock:
            txn_id = int(time.time() * 1000) + len(self.transactions)
            snapshot_version = self.version_counter
            self.transactions[txn_id] = {
                'snapshot_version': snapshot_version,
                'writes': {},
                'status': 'active',
                'start_time': time.time()
            }
            self.active_transactions.add(txn_id)
            return txn_id
    
    def read(self, txn_id, key):
        with self.lock:
            if txn_id not in self.transactions or self.transactions[txn_id]['status'] != 'active':
                raise ValueError("Invalid or inactive transaction")
            
            txn = self.transactions[txn_id]
            
            # Check if we've written this key in current transaction
            if key in txn['writes']:
                return txn['writes'][key]
            
            # Check version store for snapshot
            for version in sorted(self.versions[key].keys(), reverse=True):
                if version <= txn['snapshot_version']:
                    return self.versions[key][version]
            
            # Fall back to current data if no version found
            return self.data.get(key)
    
    def write(self, txn_id, key, value):
        with self.lock:
            if txn_id not in self.transactions or self.transactions[txn_id]['status'] != 'active':
                raise ValueError("Invalid or inactive transaction")
            
            self.transactions[txn_id]['writes'][key] = value
    
    def commit(self, txn_id):
        with self.lock:
            if txn_id not in self.transactions or self.transactions[txn_id]['status'] != 'active':
                raise ValueError("Invalid or inactive transaction")
            
            txn = self.transactions[txn_id]
            self.version_counter += 1
            commit_version = self.version_counter
            
            # Apply writes to version store
            for key, value in txn['writes'].items():
                self.versions[key][commit_version] = value
                self.data[key] = value  # Update current data
            
            txn['status'] = 'committed'
            self.active_transactions.discard(txn_id)
    
    def abort(self, txn_id):
        with self.lock:
            if txn_id not in self.transactions or self.transactions[txn_id]['status'] != 'active':
                raise ValueError("Invalid or inactive transaction")
            
            self.transactions[txn_id]['status'] = 'aborted'
            self.active_transactions.discard(txn_id)