import threading
import re

class EventCorrelator:
    def __init__(self, patterns):
        self.patterns = patterns  # list of pattern dictionaries
        self.events = []  # store ingested events as they arrive
        self.lock = threading.Lock()
        # Tolerance in milliseconds for out-of-order events
        self.tolerance = 1000

    def ingest_event(self, event):
        with self.lock:
            self.events.append(event)

    def get_alerts(self):
        with self.lock:
            # Make a sorted copy of the events list based on timestamp.
            sorted_events = sorted(self.events, key=lambda e: e["timestamp"])
            alerts = []
            # For each pattern, try to extract all non-overlapping matching sequences.
            for pattern in self.patterns:
                pattern_alerts = self.__extract_alerts_for_pattern(sorted_events, pattern)
                alerts.extend(pattern_alerts)
            # Clear events after processing.
            self.events.clear()
            return alerts

    def __match_rule(self, event, rule):
        # Check if event's source matches the regex provided in rule.
        if not re.fullmatch(rule["source"], event["source"]):
            return False
        # For each attribute in rule's attributes, check the event's attribute.
        for key, expected in rule.get("attributes", {}).items():
            if key not in event["attributes"]:
                return False
            actual = event["attributes"][key]
            if callable(expected):
                if not expected(actual):
                    return False
            else:
                if actual != expected:
                    return False
        return True

    def __extract_alerts_for_pattern(self, sorted_events, pattern):
        alerts = []
        n = len(sorted_events)
        used_indices = [False] * n  # To avoid reusing the same event in one pattern's alert.
        i = 0
        while i < n:
            # Skip events already used in a previous match for this pattern.
            if used_indices[i]:
                i += 1
                continue
            # Try to match the sequence starting at event i.
            if self.__match_rule(sorted_events[i], pattern["events"][0]):
                candidate_indices = [i]
                first_ts = sorted_events[i]["timestamp"]
                last_ts = sorted_events[i]["timestamp"]
                curr_index = i
                match_found = True
                # For remaining rules in the pattern:
                for rule_idx in range(1, len(pattern["events"])):
                    found = False
                    # Search for an event after the current event in sorted order.
                    for j in range(curr_index + 1, n):
                        # Skip events already used.
                        if used_indices[j]:
                            continue
                        if self.__match_rule(sorted_events[j], pattern["events"][rule_idx]):
                            # Check that the event is within time window from the first event.
                            if sorted_events[j]["timestamp"] - first_ts <= pattern["time_window"]:
                                # Allow out-of-order if within tolerance.
                                if sorted_events[j]["timestamp"] >= last_ts or (last_ts - sorted_events[j]["timestamp"] <= self.tolerance):
                                    candidate_indices.append(j)
                                    last_ts = max(last_ts, sorted_events[j]["timestamp"])
                                    curr_index = j
                                    found = True
                                    break
                    if not found:
                        match_found = False
                        break
                if match_found:
                    # Build the candidate alert from the candidate indices.
                    candidate_events = [sorted_events[idx] for idx in candidate_indices]
                    alerts.append({
                        "pattern_name": pattern["name"],
                        "events": candidate_events
                    })
                    # Mark these events as used for this pattern.
                    for idx in candidate_indices:
                        used_indices[idx] = True
                    # Continue search after the first candidate event index is used.
                    i = candidate_indices[0] + 1
                    continue
            i += 1
        return alerts