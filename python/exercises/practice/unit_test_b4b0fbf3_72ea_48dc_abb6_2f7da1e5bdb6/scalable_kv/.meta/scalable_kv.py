from typing import List, Tuple, Optional, Dict
from collections import defaultdict
import bisect
import threading
import pickle
import os
import time

class MemTable:
    def __init__(self, max_size_bytes: int = 4 * 1024 * 1024):  # 4MB default
        self.data: Dict[int, bytes] = {}
        self.max_size_bytes = max_size_bytes
        self.current_size_bytes = 0
        self.lock = threading.RLock()

    def put(self, key: int, value: bytes) -> bool:
        with self.lock:
            value_size = len(value)
            if key in self.data:
                self.current_size_bytes -= len(self.data[key])
            
            new_size = self.current_size_bytes + value_size
            if new_size > self.max_size_bytes:
                return False
                
            self.data[key] = value
            self.current_size_bytes = new_size
            return True

    def get(self, key: int) -> Optional[bytes]:
        with self.lock:
            return self.data.get(key)

    def range_query(self, start: int, end: int) -> List[Tuple[int, bytes]]:
        with self.lock:
            return [(k, v) for k, v in self.data.items() if start <= k <= end]

    def is_empty(self) -> bool:
        with self.lock:
            return len(self.data) == 0

    def clear(self):
        with self.lock:
            self.data.clear()
            self.current_size_bytes = 0

class SSTable:
    def __init__(self, level: int, file_id: int, base_path: str = "./data"):
        self.level = level
        self.file_id = file_id
        self.base_path = base_path
        self.filename = f"{base_path}/L{level}-{file_id}.sst"
        self.index: List[int] = []  # Sorted list of keys
        self.data: Dict[int, bytes] = {}
        
    def write(self, data: Dict[int, bytes]):
        os.makedirs(self.base_path, exist_ok=True)
        self.data = data
        self.index = sorted(data.keys())
        
        with open(self.filename, 'wb') as f:
            pickle.dump((self.index, self.data), f)

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                self.index, self.data = pickle.load(f)

    def get(self, key: int) -> Optional[bytes]:
        return self.data.get(key)

    def range_query(self, start: int, end: int) -> List[Tuple[int, bytes]]:
        start_idx = bisect.bisect_left(self.index, start)
        end_idx = bisect.bisect_right(self.index, end)
        
        result = []
        for idx in range(start_idx, end_idx):
            key = self.index[idx]
            result.append((key, self.data[key]))
        return result

class KVStore:
    def __init__(self, base_path: str = "./data"):
        self.memtable = MemTable()
        self.immutable_memtable = None
        self.sstables: List[List[SSTable]] = [[] for _ in range(7)]  # L0 to L6
        self.base_path = base_path
        self.next_file_id = 0
        self.lock = threading.Lock()
        self.compaction_thread = threading.Thread(target=self._background_compaction, daemon=True)
        self.compaction_thread.start()
        self._load_existing_sstables()

    def _load_existing_sstables(self):
        if not os.path.exists(self.base_path):
            return
            
        for filename in os.listdir(self.base_path):
            if filename.endswith('.sst'):
                level = int(filename[1])
                file_id = int(filename.split('-')[1].split('.')[0])
                self.next_file_id = max(self.next_file_id, file_id + 1)
                
                sstable = SSTable(level, file_id, self.base_path)
                sstable.load()
                self.sstables[level].append(sstable)

    def put(self, key: int, value: bytes):
        if len(value) > 1024:  # 1KB limit
            raise ValueError("Value size exceeds 1KB limit")
            
        if not self.memtable.put(key, value):
            with self.lock:
                if self.immutable_memtable is None:
                    self.immutable_memtable = self.memtable
                    self.memtable = MemTable()
                    self._flush_immutable_memtable()
                else:
                    # Wait for ongoing flush to complete
                    while self.immutable_memtable is not None:
                        time.sleep(0.1)
                    self.put(key, value)  # Retry

    def get(self, key: int) -> Optional[bytes]:
        # Check memtable first
        value = self.memtable.get(key)
        if value is not None:
            return value
            
        # Check immutable memtable
        if self.immutable_memtable:
            value = self.immutable_memtable.get(key)
            if value is not None:
                return value
        
        # Check SSTable levels from newest to oldest
        for level in range(len(self.sstables)):
            for sstable in reversed(self.sstables[level]):
                value = sstable.get(key)
                if value is not None:
                    return value
        
        return None

    def range_query(self, start: int, end: int) -> List[Tuple[int, bytes]]:
        if start > end:
            raise ValueError("Start timestamp must be less than or equal to end timestamp")
            
        results = []
        
        # Query memtable
        results.extend(self.memtable.range_query(start, end))
        
        # Query immutable memtable if exists
        if self.immutable_memtable:
            results.extend(self.immutable_memtable.range_query(start, end))
        
        # Query all SSTables
        for level in range(len(self.sstables)):
            for sstable in self.sstables[level]:
                results.extend(sstable.range_query(start, end))
        
        # Remove duplicates keeping only the latest version
        seen_keys = set()
        unique_results = []
        
        for key, value in sorted(results, reverse=True):
            if key not in seen_keys:
                seen_keys.add(key)
                unique_results.append((key, value))
        
        return sorted(unique_results)

    def _flush_immutable_memtable(self):
        if not self.immutable_memtable or self.immutable_memtable.is_empty():
            self.immutable_memtable = None
            return
            
        # Create new L0 SSTable
        sstable = SSTable(0, self.next_file_id, self.base_path)
        self.next_file_id += 1
        
        # Write memtable data to SSTable
        sstable.write(self.immutable_memtable.data)
        self.sstables[0].append(sstable)
        
        self.immutable_memtable = None
        
        # Trigger compaction if needed
        if len(self.sstables[0]) > 4:  # L0 compaction threshold
            self._compact_level(0)

    def _compact_level(self, level: int):
        if level >= len(self.sstables) - 1:
            return
            
        # Merge all SSTables at current level
        merged_data = {}
        for sstable in self.sstables[level]:
            merged_data.update(sstable.data)
        
        # Split into smaller SSTables for next level
        max_sstable_size = 10 * (4 * 1024 * 1024) * (level + 1)  # Size increases with level
        current_data = {}
        current_size = 0
        
        for key in sorted(merged_data.keys()):
            value = merged_data[key]
            value_size = len(value)
            
            if current_size + value_size > max_sstable_size:
                # Create new SSTable
                sstable = SSTable(level + 1, self.next_file_id, self.base_path)
                self.next_file_id += 1
                sstable.write(current_data)
                self.sstables[level + 1].append(sstable)
                
                current_data = {}
                current_size = 0
            
            current_data[key] = value
            current_size += value_size
        
        # Write remaining data
        if current_data:
            sstable = SSTable(level + 1, self.next_file_id, self.base_path)
            self.next_file_id += 1
            sstable.write(current_data)
            self.sstables[level + 1].append(sstable)
        
        # Remove old SSTables
        for sstable in self.sstables[level]:
            os.remove(sstable.filename)
        self.sstables[level].clear()
        
        # Check if next level needs compaction
        if len(self.sstables[level + 1]) > 4 * (level + 1):
            self._compact_level(level + 1)

    def _background_compaction(self):
        while True:
            time.sleep(1)
            with self.lock:
                if self.immutable_memtable is not None:
                    self._flush_immutable_memtable()
                
                for level in range(len(self.sstables) - 1):
                    if len(self.sstables[level]) > 4 * (level + 1):
                        self._compact_level(level)