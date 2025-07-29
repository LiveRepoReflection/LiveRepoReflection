import os
import re
import shelve
import threading
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Optional, Set

class LogAggregator:
    def __init__(self, storage_path: str = "log_storage"):
        self.storage_path = storage_path
        self.lock = threading.Lock()
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Initialize storage files
        self.log_store = shelve.open(os.path.join(self.storage_path, "logs"))
        self.index_store = shelve.open(os.path.join(self.storage_path, "index"))
        self.timestamp_index = shelve.open(os.path.join(self.storage_path, "timestamps"))
        
        # Initialize in-memory structures for faster access
        self.field_indexes = {
            "level": defaultdict(set),
            "ip": defaultdict(set),
        }
        self.log_count = 0

    def __len__(self):
        return self.log_count

    def ingest(self, log_entry: str):
        try:
            timestamp_str, level, ip, message = log_entry.split("|", 3)
            timestamp = datetime.fromisoformat(timestamp_str.rstrip("Z"))
        except (ValueError, AttributeError):
            raise ValueError("Malformed log entry format")

        with self.lock:
            log_id = f"log_{self.log_count}"
            log_data = {
                "timestamp": timestamp_str,
                "level": level,
                "ip": ip,
                "message": message
            }
            
            # Store the log
            self.log_store[log_id] = log_data
            self.timestamp_index[log_id] = timestamp_str
            
            # Update indexes
            self._update_indexes(log_id, level, ip, timestamp_str)
            self.log_count += 1

    def _update_indexes(self, log_id: str, level: str, ip: str, timestamp: str):
        # Update field indexes
        self.field_indexes["level"][level].add(log_id)
        self.field_indexes["ip"][ip].add(log_id)
        
        # Update persistent index store
        if "level" not in self.index_store:
            self.index_store["level"] = {}
        if "ip" not in self.index_store:
            self.index_store["ip"] = {}
            
        self.index_store["level"][level] = list(self.field_indexes["level"][level])
        self.index_store["ip"][ip] = list(self.field_indexes["ip"][ip])

    def query(self, query_str: str) -> List[str]:
        conditions = self._parse_query(query_str)
        result_ids = self._execute_query(conditions)
        
        results = []
        for log_id in result_ids:
            log_data = self.log_store[log_id]
            results.append(f"{log_data['timestamp']}|{log_data['level']}|{log_data['ip']}|{log_data['message']}")
        
        return results

    def _parse_query(self, query_str: str) -> List[Dict[str, str]]:
        conditions = []
        for condition in query_str.split(" AND "):
            or_conditions = condition.split(" OR ")
            for or_cond in or_conditions:
                if ":" in or_cond:
                    field, value = or_cond.split(":", 1)
                    conditions.append({"field": field.strip(), "value": value.strip(), "operator": "OR" if len(or_conditions) > 1 else "AND"})
        return conditions

    def _execute_query(self, conditions: List[Dict[str, str]]) -> Set[str]:
        result_ids = set()
        first_condition = True
        
        for condition in conditions:
            field = condition["field"]
            value = condition["value"]
            operator = condition["operator"]
            
            if field in self.field_indexes:
                matching_ids = set(self.field_indexes[field].get(value, []))
            else:
                matching_ids = set()
                
            if first_condition:
                result_ids = matching_ids
                first_condition = False
            else:
                if operator == "AND":
                    result_ids &= matching_ids
                else:  # OR
                    result_ids |= matching_ids
        
        return result_ids

    def apply_retention_policy(self, retention_period: timedelta):
        cutoff_time = datetime.utcnow() - retention_period
        
        with self.lock:
            logs_to_remove = []
            for log_id, timestamp_str in self.timestamp_index.items():
                timestamp = datetime.fromisoformat(timestamp_str.rstrip("Z"))
                if timestamp < cutoff_time:
                    logs_to_remove.append(log_id)
            
            for log_id in logs_to_remove:
                self._remove_log(log_id)

    def _remove_log(self, log_id: str):
        if log_id in self.log_store:
            log_data = self.log_store[log_id]
            
            # Remove from indexes
            self.field_indexes["level"][log_data["level"]].discard(log_id)
            self.field_indexes["ip"][log_data["ip"]].discard(log_id)
            
            # Remove from storage
            del self.log_store[log_id]
            del self.timestamp_index[log_id]
            self.log_count -= 1

    def aggregate(self, field: str, filter: Optional[str] = None, 
                 start_time: Optional[datetime] = None, 
                 end_time: Optional[datetime] = None) -> Dict[str, int]:
        aggregation = defaultdict(int)
        filter_ids = None
        
        if filter:
            filter_ids = self._execute_query(self._parse_query(filter))
        
        for log_id, log_data in self.log_store.items():
            timestamp = datetime.fromisoformat(log_data["timestamp"].rstrip("Z"))
            
            # Apply time filter if specified
            if start_time and timestamp < start_time:
                continue
            if end_time and timestamp > end_time:
                continue
            
            # Apply query filter if specified
            if filter_ids and log_id not in filter_ids:
                continue
            
            # Aggregate by specified field
            if field in log_data:
                aggregation[log_data[field]] += 1
        
        return dict(aggregation)

    def close(self):
        self.log_store.close()
        self.index_store.close()
        self.timestamp_index.close()

    def __del__(self):
        self.close()