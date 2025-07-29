import unittest
import threading
import time
import re

# Assume that the implementation exists in event_correlator.py and provides the following interface:
#   class EventCorrelator:
#       def __init__(self, patterns: list):
#           ...
#       def ingest_event(self, event: dict) -> None:
#           ...
#       def get_alerts(self) -> list:
#           ...
#
# For unit testing purposes we assume that each alert is a dictionary with keys:
#   'pattern_name': str, 
#   'events': list of events (in the order they were matched)

from event_correlator.event_correlator import EventCorrelator

class EventCorrelatorTest(unittest.TestCase):
    def setUp(self):
        # Define a pattern to detect a suspicious login:
        # A "login_failed" event followed by a "login_success" event for a specific user ('john.doe').
        self.suspicious_login_pattern = {
            "name": "SuspiciousLogin",
            "time_window": 60000,  # 60 seconds
            "events": [
                {
                    "source": ".*",
                    "attributes": {
                        "event_type": "login_failed",
                        "user": "john.doe"
                    }
                },
                {
                    "source": ".*",
                    "attributes": {
                        "event_type": "login_success",
                        "user": "john.doe"
                    }
                }
            ]
        }
        
        # Define another pattern for detecting out-of-bound alerts:
        # Two events with a numerical attribute increasing by at least 10 within 30 seconds.
        self.increase_pattern = {
            "name": "RapidIncrease",
            "time_window": 30000,  # 30 seconds
            "events": [
                {
                    "source": "sensor_[0-9]+",
                    "attributes": {
                        "event_type": "reading",
                        "value": lambda x: isinstance(x, (int, float))
                    }
                },
                {
                    "source": "sensor_[0-9]+",
                    "attributes": {
                        "event_type": "reading",
                        "value": lambda x: isinstance(x, (int, float))
                    }
                }
            ]
        }
        
    def matches_rule(self, event, rule):
        """
        Helper function to check if event satisfies a given rule from the pattern.
        The rule has 'source' to be matched as regex and 'attributes' dict where values can be either
        a literal for equality or a callable for validation.
        """
        if not re.fullmatch(rule["source"], event["source"]):
            return False
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

    def test_no_alert_for_incomplete_sequence(self):
        # Initialize correlator with one pattern
        ec = EventCorrelator(patterns=[self.suspicious_login_pattern])
        # Feed only one event (login_failed) without a matching login_success
        event = {
            "timestamp": 1609459200000,
            "source": "server1",
            "attributes": {
                "event_type": "login_failed",
                "user": "john.doe",
                "ip_address": "192.168.1.100"
            }
        }
        ec.ingest_event(event)
        # Allow time for processing if asynchronous
        time.sleep(0.05)
        alerts = ec.get_alerts()
        self.assertEqual(len(alerts), 0, "No alert should be generated for incomplete sequence.")

    def test_alert_trigger_on_valid_sequence(self):
        ec = EventCorrelator(patterns=[self.suspicious_login_pattern])
        base_time = 1609459200000
        # First event: login_failed
        event1 = {
            "timestamp": base_time,
            "source": "server2",
            "attributes": {
                "event_type": "login_failed",
                "user": "john.doe",
                "ip_address": "192.168.1.101"
            }
        }
        # Second event: login_success within time window
        event2 = {
            "timestamp": base_time + 30000,  # 30 seconds later
            "source": "server2",
            "attributes": {
                "event_type": "login_success",
                "user": "john.doe",
                "ip_address": "192.168.1.101"
            }
        }
        ec.ingest_event(event1)
        ec.ingest_event(event2)
        time.sleep(0.05)
        alerts = ec.get_alerts()
        self.assertEqual(len(alerts), 1, "One alert should be triggered for valid sequence.")
        alert = alerts[0]
        self.assertEqual(alert["pattern_name"], "SuspiciousLogin")
        self.assertEqual(len(alert["events"]), 2)
        # Check that events in alert match expected order via helper
        self.assertTrue(self.matches_rule(alert["events"][0], self.suspicious_login_pattern["events"][0]))
        self.assertTrue(self.matches_rule(alert["events"][1], self.suspicious_login_pattern["events"][1]))

    def test_alert_not_triggered_if_out_of_time_window(self):
        ec = EventCorrelator(patterns=[self.suspicious_login_pattern])
        base_time = 1609459200000
        # First event: login_failed
        event1 = {
            "timestamp": base_time,
            "source": "server3",
            "attributes": {
                "event_type": "login_failed",
                "user": "john.doe",
                "ip_address": "192.168.1.102"
            }
        }
        # Second event: login_success after time window (61 seconds later)
        event2 = {
            "timestamp": base_time + 61000,
            "source": "server3",
            "attributes": {
                "event_type": "login_success",
                "user": "john.doe",
                "ip_address": "192.168.1.102"
            }
        }
        ec.ingest_event(event1)
        ec.ingest_event(event2)
        time.sleep(0.05)
        alerts = ec.get_alerts()
        self.assertEqual(len(alerts), 0, "No alert should be triggered if events exceed time window.")
        
    def test_handling_out_of_order_events_within_tolerance(self):
        ec = EventCorrelator(patterns=[self.suspicious_login_pattern])
        base_time = 1609459200000
        # Events arriving out-of-order but within acceptable skew (assume tolerance: 1000 ms)
        event1 = {
            "timestamp": base_time + 1000,  # Slightly later than event2
            "source": "server4",
            "attributes": {
                "event_type": "login_success",
                "user": "john.doe",
                "ip_address": "192.168.1.103"
            }
        }
        event2 = {
            "timestamp": base_time,  # login_failed with earlier timestamp
            "source": "server4",
            "attributes": {
                "event_type": "login_failed",
                "user": "john.doe",
                "ip_address": "192.168.1.103"
            }
        }
        # Ingest out-of-order
        ec.ingest_event(event1)
        ec.ingest_event(event2)
        time.sleep(0.05)
        alerts = ec.get_alerts()
        # Expect alert if engine can rearrange events that are within 1 sec skew tolerance.
        # Otherwise, no alert should be triggered.
        if alerts:
            self.assertEqual(len(alerts), 1, "One alert should be triggered with out-of-order events within tolerance.")
            alert = alerts[0]
            self.assertEqual(alert["pattern_name"], "SuspiciousLogin")
            self.assertEqual(len(alert["events"]), 2)
        else:
            # If not implemented to re-order, then no alert is acceptable.
            self.assertEqual(len(alerts), 0, "No alert triggered if out-of-order handling is not supported.")

    def test_multiple_patterns_triggered(self):
        ec = EventCorrelator(patterns=[self.suspicious_login_pattern, self.increase_pattern])
        base_time = 1609459200000
        # Events for suspicious login pattern
        event1 = {
            "timestamp": base_time,
            "source": "server5",
            "attributes": {
                "event_type": "login_failed",
                "user": "john.doe",
            }
        }
        event2 = {
            "timestamp": base_time + 20000,  # 20 sec later
            "source": "server5",
            "attributes": {
                "event_type": "login_success",
                "user": "john.doe",
            }
        }
        # Events for rapid increase pattern. We'll use sensor_8 as source.
        event3 = {
            "timestamp": base_time + 5000,
            "source": "sensor_8",
            "attributes": {
                "event_type": "reading",
                "value": 50
            }
        }
        event4 = {
            "timestamp": base_time + 10000,
            "source": "sensor_8",
            "attributes": {
                "event_type": "reading",
                "value": 65  # Increase by 15, which is >= 10
            }
        }
        ec.ingest_event(event1)
        ec.ingest_event(event3)
        ec.ingest_event(event2)
        ec.ingest_event(event4)
        time.sleep(0.05)
        alerts = ec.get_alerts()
        # We expect 2 alerts, one for each pattern.
        self.assertEqual(len(alerts), 2, "Two alerts should be triggered for multiple patterns.")
        pattern_names = {alert["pattern_name"] for alert in alerts}
        self.assertIn("SuspiciousLogin", pattern_names)
        self.assertIn("RapidIncrease", pattern_names)

    def test_concurrent_event_ingestion(self):
        ec = EventCorrelator(patterns=[self.suspicious_login_pattern])
        base_time = 1609459200000
        
        def ingest_events(events):
            for evt in events:
                ec.ingest_event(evt)
                # simulate slight delay
                time.sleep(0.001)
                
        # Prepare two sequences that should both trigger alerts
        events_seq1 = [
            {
                "timestamp": base_time,
                "source": "server6",
                "attributes": {
                    "event_type": "login_failed",
                    "user": "john.doe",
                }
            },
            {
                "timestamp": base_time + 10000,
                "source": "server6",
                "attributes": {
                    "event_type": "login_success",
                    "user": "john.doe",
                }
            }
        ]
        
        events_seq2 = [
            {
                "timestamp": base_time + 2000,
                "source": "server7",
                "attributes": {
                    "event_type": "login_failed",
                    "user": "john.doe",
                }
            },
            {
                "timestamp": base_time + 12000,
                "source": "server7",
                "attributes": {
                    "event_type": "login_success",
                    "user": "john.doe",
                }
            }
        ]
        
        thread1 = threading.Thread(target=ingest_events, args=(events_seq1,))
        thread2 = threading.Thread(target=ingest_events, args=(events_seq2,))
        
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        
        time.sleep(0.05)
        alerts = ec.get_alerts()
        self.assertEqual(len(alerts), 2, "Two alerts should be triggered for concurrent ingestion.")

if __name__ == '__main__':
    unittest.main()