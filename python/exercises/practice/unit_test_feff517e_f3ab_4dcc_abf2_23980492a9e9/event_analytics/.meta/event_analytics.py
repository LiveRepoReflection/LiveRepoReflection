from collections import defaultdict
import heapq
from datetime import datetime
import threading
from typing import Dict, List, Tuple, Optional
import json

class EventAnalytics:
    def __init__(self):
        # In-memory cache for recent events
        self._cache = []
        self._cache_lock = threading.Lock()
        
        # Index structures for efficient querying
        self._device_index = defaultdict(list)  # device_id -> events
        self._type_index = defaultdict(list)    # event_type -> events
        self._geo_index = defaultdict(list)     # grid_cell -> events
        
        # Constants for geo-indexing
        self.GEO_GRID_SIZE = 0.1  # degrees
        
        # Cache configuration
        self.MAX_CACHE_SIZE = 1000000  # Maximum number of events in memory
        
    def _get_grid_cell(self, lat: float, lon: float) -> Tuple[int, int]:
        """Convert latitude and longitude to grid cell coordinates."""
        return (
            int(lat / self.GEO_GRID_SIZE),
            int(lon / self.GEO_GRID_SIZE)
        )
        
    def ingest_event(self, event: dict) -> None:
        """Ingest a new event into the system."""
        with self._cache_lock:
            # Add to main cache
            self._cache.append(event)
            
            # Update indices
            self._device_index[event['device_id']].append(event)
            self._type_index[event['type']].append(event)
            
            grid_cell = self._get_grid_cell(
                event['location']['latitude'],
                event['location']['longitude']
            )
            self._geo_index[grid_cell].append(event)
            
            # Implement cache eviction if necessary
            if len(self._cache) > self.MAX_CACHE_SIZE:
                self._evict_old_events()

    def _evict_old_events(self) -> None:
        """Remove oldest events when cache is full."""
        # Sort by timestamp and keep only recent events
        self._cache.sort(key=lambda x: x['timestamp'])
        self._cache = self._cache[-self.MAX_CACHE_SIZE:]
        
        # Rebuild indices
        self._rebuild_indices()

    def _rebuild_indices(self) -> None:
        """Rebuild all index structures."""
        self._device_index.clear()
        self._type_index.clear()
        self._geo_index.clear()
        
        for event in self._cache:
            self._device_index[event['device_id']].append(event)
            self._type_index[event['type']].append(event)
            grid_cell = self._get_grid_cell(
                event['location']['latitude'],
                event['location']['longitude']
            )
            self._geo_index[grid_cell].append(event)

    def get_average_by_time_window(
        self,
        device_id: str,
        event_type: str,
        start_time: int,
        end_time: int
    ) -> float:
        """Calculate average value for a device and type within time window."""
        if start_time >= end_time:
            raise ValueError("Invalid time window")
            
        values = []
        events = self._device_index[device_id]
        
        for event in events:
            if (event['type'] == event_type and
                start_time <= event['timestamp'] <= end_time):
                values.append(event['value'])
                
        if not values:
            return 0.0
            
        return sum(values) / len(values)

    def get_top_k_devices(
        self,
        k: int,
        event_type: str,
        start_time: int,
        end_time: int
    ) -> List[Tuple[str, int]]:
        """Get top K devices by event count for a type within time window."""
        if k <= 0:
            raise ValueError("Invalid k value")
            
        device_counts = defaultdict(int)
        events = self._type_index[event_type]
        
        for event in events:
            if start_time <= event['timestamp'] <= end_time:
                device_counts[event['device_id']] += 1
                
        # Use heap to get top K efficiently
        return heapq.nlargest(
            k,
            device_counts.items(),
            key=lambda x: x[1]
        )

    def get_geospatial_average(
        self,
        event_type: str,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        start_time: int,
        end_time: int
    ) -> float:
        """Calculate average value within geographical bounds and time window."""
        if min_lat >= max_lat or min_lon >= max_lon:
            raise ValueError("Invalid geographical bounds")
            
        values = []
        
        # Get relevant grid cells
        min_cell = self._get_grid_cell(min_lat, min_lon)
        max_cell = self._get_grid_cell(max_lat, max_lon)
        
        for i in range(min_cell[0], max_cell[0] + 1):
            for j in range(min_cell[1], max_cell[1] + 1):
                events = self._geo_index[(i, j)]
                
                for event in events:
                    if (event['type'] == event_type and
                        start_time <= event['timestamp'] <= end_time and
                        min_lat <= event['location']['latitude'] <= max_lat and
                        min_lon <= event['location']['longitude'] <= max_lon):
                        values.append(event['value'])
                        
        if not values:
            return 0.0
            
        return sum(values) / len(values)

    def _validate_event(self, event: dict) -> bool:
        """Validate event structure and data types."""
        required_fields = {
            'device_id': str,
            'timestamp': int,
            'type': str,
            'value': (int, float),
            'location': dict
        }
        
        try:
            for field, field_type in required_fields.items():
                if field not in event:
                    return False
                if not isinstance(event[field], field_type):
                    return False
                    
            location = event['location']
            if not all(k in location for k in ('latitude', 'longitude')):
                return False
                
            if not isinstance(location['latitude'], (int, float)):
                return False
            if not isinstance(location['longitude'], (int, float)):
                return False
                
            return True
        except Exception:
            return False