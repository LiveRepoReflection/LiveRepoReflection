import os
import sqlite3
import json
import time
from collections import defaultdict
from typing import Dict, List, Optional, Union

class AnalyticsEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._initialize_db()
        self.in_memory_cache = defaultdict(list)
        self.last_save_time = time.time()

    def _initialize_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                user_id INTEGER,
                event_type TEXT,
                timestamp INTEGER,
                data TEXT,
                PRIMARY KEY (user_id, timestamp, event_type)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)')
        self.conn.commit()

    def record_event(self, user_id: int, event_type: str, timestamp: int, data: Dict):
        # Add to in-memory cache first
        self.in_memory_cache[(user_id, event_type, timestamp)].append(data)
        
        # Periodically flush to disk
        if time.time() - self.last_save_time > 60:  # Save every minute
            self.save_data()

    def get_aggregate(self, metric: str, window_size: int, start_time: int, end_time: int, 
                     field_name: Optional[str] = None) -> Union[int, float]:
        # Combine in-memory and on-disk data
        events = self._query_events(start_time, end_time)
        
        if metric == "event_count":
            return len(events)
        
        elif metric == "unique_users":
            return len({e[0] for e in events})
        
        elif metric == "average_data_value" and field_name:
            values = []
            for event in events:
                try:
                    data = json.loads(event[3])
                    if field_name in data:
                        values.append(float(data[field_name]))
                except (json.JSONDecodeError, ValueError):
                    continue
            return sum(values) / len(values) if values else 0
        
        raise ValueError(f"Unsupported metric: {metric}")

    def _query_events(self, start_time: int, end_time: int) -> List[tuple]:
        # Get from in-memory cache
        in_memory_events = []
        for (user_id, event_type, ts), data_list in self.in_memory_cache.items():
            if start_time <= ts <= end_time:
                for data in data_list:
                    in_memory_events.append((user_id, event_type, ts, json.dumps(data)))
        
        # Get from database
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_id, event_type, timestamp, data 
            FROM events 
            WHERE timestamp BETWEEN ? AND ?
        ''', (start_time, end_time))
        db_events = cursor.fetchall()
        
        return in_memory_events + db_events

    def save_data(self):
        cursor = self.conn.cursor()
        for (user_id, event_type, ts), data_list in self.in_memory_cache.items():
            for data in data_list:
                cursor.execute('''
                    INSERT OR IGNORE INTO events (user_id, event_type, timestamp, data)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, event_type, ts, json.dumps(data)))
        self.conn.commit()
        self.in_memory_cache.clear()
        self.last_save_time = time.time()

    def load_data(self):
        # No need to load all data into memory - we query from disk as needed
        pass

    def cleanup_expired_events(self):
        expiration_time = int(time.time()) - (30 * 24 * 3600)
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM events WHERE timestamp < ?', (expiration_time,))
        self.conn.commit()

    def close(self):
        self.save_data()
        self.conn.close()