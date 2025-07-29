from collections import defaultdict
from bisect import insort, bisect_left, bisect_right
from typing import Dict, List, Set, Tuple

class LogAnalysisSystem:
    def __init__(self):
        # Dictionary to store logs by machine_id
        # Each machine's logs are stored in a sorted list by timestamp
        self.logs_by_machine: Dict[str, List[Tuple[int, str, str, str]]] = defaultdict(list)
        
        # Dictionary to store timestamp to log entry mapping for each machine
        # This helps in quick retrieval of logs within a time range
        self.timestamp_index: Dict[str, Dict[int, List[Tuple[int, str, str, str]]]] = defaultdict(lambda: defaultdict(list))

    def process_log_entry(self, timestamp: int, machine_id: str, log_level: str, message: str) -> None:
        """
        Process a new log entry and store it in the system.
        Time complexity: O(log n) where n is the number of logs for the machine
        Space complexity: O(1) for each log entry
        """
        log_entry = (timestamp, machine_id, log_level, message)
        
        # Insert into sorted list maintaining order
        insort(self.logs_by_machine[machine_id], log_entry)
        
        # Add to timestamp index
        self.timestamp_index[machine_id][timestamp].append(log_entry)

    def query_logs(self, start_time: int, end_time: int, machine_ids: Set[str]) -> List[Tuple[int, str, str, str]]:
        """
        Query logs within the given time range for specified machines.
        Returns sorted list of log entries.
        Time complexity: O(m * log n + k) where:
            m is the number of machine_ids
            n is the number of logs per machine
            k is the number of logs in the result
        Space complexity: O(k) where k is the size of the result
        """
        if not machine_ids:
            return []

        result = []
        
        for machine_id in machine_ids:
            if machine_id not in self.logs_by_machine:
                continue

            machine_logs = self.logs_by_machine[machine_id]
            
            # Find the range of indices that contain logs within our time range
            # Using binary search for efficiency
            start_idx = bisect_left(machine_logs, (start_time, '', '', ''))
            end_idx = bisect_right(machine_logs, (end_time + 1, '', '', ''))
            
            # Add all logs within the range
            result.extend(machine_logs[start_idx:end_idx])

        # Sort all collected logs by timestamp
        return sorted(result, key=lambda x: x[0])

    def _get_logs_in_timerange(self, machine_id: str, start_time: int, end_time: int) -> List[Tuple[int, str, str, str]]:
        """
        Helper method to get logs for a specific machine within a time range.
        """
        if machine_id not in self.logs_by_machine:
            return []
            
        logs = []
        machine_timestamps = self.timestamp_index[machine_id]
        
        for timestamp in range(start_time, end_time + 1):
            if timestamp in machine_timestamps:
                logs.extend(machine_timestamps[timestamp])
                
        return logs