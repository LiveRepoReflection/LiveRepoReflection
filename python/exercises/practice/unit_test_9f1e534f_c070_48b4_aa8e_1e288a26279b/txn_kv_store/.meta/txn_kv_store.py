import json
import threading
import time
from typing import Dict, Optional, Any
from dataclasses import dataclass
from threading import Lock

@dataclass
class KeyMetadata:
    value: str
    timestamp: int

@dataclass
class Transaction:
    txid: int
    start_timestamp: int
    staged_changes: Dict[str, str]
    read_timestamps: Dict[str, int]
    status: str  # 'active', 'committed', 'aborted'

class TransactionalKeyValueStore:
    def __init__(self, num_nodes: int):
        self.num_nodes = num_nodes
        self.data: Dict[str, KeyMetadata] = {}
        self.transactions: Dict[int, Transaction] = {}
        self.global_timestamp = 0
        self.next_txid = 1
        
        # Locks
        self.data_lock = Lock()
        self.tx_lock = Lock()
        self.timestamp_lock = Lock()
        self.txid_lock = Lock()

    def _get_next_timestamp(self) -> int:
        with self.timestamp_lock:
            self.global_timestamp += 1
            return self.global_timestamp

    def _get_next_txid(self) -> int:
        with self.txid_lock:
            txid = self.next_txid
            self.next_txid += 1
            return txid

    def begin_transaction(self) -> int:
        txid = self._get_next_txid()
        timestamp = self._get_next_timestamp()
        
        with self.tx_lock:
            self.transactions[txid] = Transaction(
                txid=txid,
                start_timestamp=timestamp,
                staged_changes={},
                read_timestamps={},
                status='active'
            )
        return txid

    def get(self, txid: int, key: str) -> Optional[str]:
        with self.tx_lock:
            if txid not in self.transactions:
                raise ValueError(f"Transaction {txid} does not exist")
            
            tx = self.transactions[txid]
            if tx.status != 'active':
                raise ValueError(f"Transaction {txid} is not active")

            # Check staged changes first
            if key in tx.staged_changes:
                return tx.staged_changes[key]

        # Read from main storage
        with self.data_lock:
            if key in self.data:
                metadata = self.data[key]
                # Record the timestamp at which we read this key
                with self.tx_lock:
                    tx.read_timestamps[key] = metadata.timestamp
                return metadata.value
            return None

    def put(self, txid: int, key: str, value: str) -> None:
        with self.tx_lock:
            if txid not in self.transactions:
                raise ValueError(f"Transaction {txid} does not exist")
            
            tx = self.transactions[txid]
            if tx.status != 'active':
                raise ValueError(f"Transaction {txid} is not active")

            # Record the read timestamp if we haven't accessed this key before
            if key not in tx.read_timestamps:
                with self.data_lock:
                    tx.read_timestamps[key] = self.data[key].timestamp if key in self.data else 0

            # Stage the change
            tx.staged_changes[key] = value

    def commit_transaction(self, txid: int) -> bool:
        with self.tx_lock:
            if txid not in self.transactions:
                raise ValueError(f"Transaction {txid} does not exist")
            
            tx = self.transactions[txid]
            if tx.status != 'active':
                raise ValueError(f"Transaction {txid} is not in active state")

            # Check for conflicts
            with self.data_lock:
                for key in tx.staged_changes.keys():
                    current_timestamp = self.data[key].timestamp if key in self.data else 0
                    if current_timestamp != tx.read_timestamps.get(key, 0):
                        tx.status = 'aborted'
                        return False

                # No conflicts, commit changes
                commit_timestamp = self._get_next_timestamp()
                for key, value in tx.staged_changes.items():
                    self.data[key] = KeyMetadata(value=value, timestamp=commit_timestamp)

                tx.status = 'committed'
                self._persist_state()
                return True

    def abort_transaction(self, txid: int) -> None:
        with self.tx_lock:
            if txid not in self.transactions:
                raise ValueError(f"Transaction {txid} does not exist")
            
            tx = self.transactions[txid]
            if tx.status != 'active':
                raise ValueError(f"Transaction {txid} is not active")
            
            tx.status = 'aborted'

    def recover(self) -> None:
        try:
            with open('state.json', 'r') as f:
                state = json.load(f)
                
            with self.data_lock:
                self.data = {
                    k: KeyMetadata(v['value'], v['timestamp']) 
                    for k, v in state['data'].items()
                }
            
            with self.txid_lock:
                self.next_txid = state['next_txid']
            
            with self.timestamp_lock:
                self.global_timestamp = state['global_timestamp']
                
        except FileNotFoundError:
            pass

    def _persist_state(self) -> None:
        state = {
            'data': {
                k: {'value': v.value, 'timestamp': v.timestamp}
                for k, v in self.data.items()
            },
            'next_txid': self.next_txid,
            'global_timestamp': self.global_timestamp
        }
        
        with open('state.json', 'w') as f:
            json.dump(state, f)