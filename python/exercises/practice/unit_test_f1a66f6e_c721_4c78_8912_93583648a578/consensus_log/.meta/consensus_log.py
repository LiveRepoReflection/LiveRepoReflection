from dataclasses import dataclass
from typing import List
from threading import Lock

@dataclass(frozen=True)
class LogEntry:
    term: int
    index: int
    command: str

class Node:
    def __init__(self, node_id: int):
        self._node_id = node_id
        self._current_term = 1
        self._log: List[LogEntry] = []
        self._lock = Lock()  # For thread safety

    def get_current_term(self) -> int:
        with self._lock:
            return self._current_term

    def set_current_term(self, term: int) -> None:
        with self._lock:
            if term > self._current_term:
                self._current_term = term

    def get_log(self) -> List[LogEntry]:
        with self._lock:
            return self._log.copy()  # Return a copy to prevent external modifications

    def append_entry(self, entry: LogEntry) -> bool:
        with self._lock:
            # Validate term
            if entry.term < self._current_term:
                return False

            # Validate index
            expected_index = len(self._log) + 1
            if entry.index != expected_index:
                return False

            # Append the entry
            self._log.append(entry)
            return True

    def accept_proposal(self, term: int, prev_log_index: int, prev_log_term: int, entry: LogEntry) -> bool:
        with self._lock:
            # Update term if necessary
            if term > self._current_term:
                self._current_term = term

            # Reject if term is less than current term
            if term < self._current_term:
                return False

            # Special case for first entry
            if prev_log_index == 0 and entry.index == 1:
                if not self._log:
                    self._log.append(entry)
                    return True
                else:
                    # If we already have entries, only accept if this would replace everything
                    self._log = [entry]
                    return True

            # Verify previous log entry matches
            if prev_log_index > 0:
                if prev_log_index > len(self._log):
                    return False
                if prev_log_index > 0 and self._log[prev_log_index - 1].term != prev_log_term:
                    return False

            # Verify entry index is correct
            if entry.index != prev_log_index + 1:
                return False

            # Handle conflicts: if we find an existing entry with same index but different term,
            # remove it and all that follow
            if entry.index <= len(self._log):
                if self._log[entry.index - 1].term != entry.term:
                    self._log = self._log[:entry.index - 1]
                    self._log.append(entry)
                return True
            elif entry.index == len(self._log) + 1:
                self._log.append(entry)
                return True
            else:
                return False