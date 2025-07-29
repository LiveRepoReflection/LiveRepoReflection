import unittest
from packet_scheduler import schedule_packets

class PacketSchedulerTest(unittest.TestCase):
    def test_single_packet(self):
        arrival_time = [0]
        priority = [10]
        deadline = [5]
        processing_time = [2]
        result = schedule_packets(arrival_time, priority, deadline, processing_time)
        self.assertEqual(result, [0])

    def test_basic_schedule(self):
        # Example from the problem description
        arrival_time = [0, 1, 2, 3]
        priority = [10, 5, 8, 2]
        deadline = [10, 5, 12, 6]
        processing_time = [3, 2, 4, 1]
        result = schedule_packets(arrival_time, priority, deadline, processing_time)
        self.assertEqual(result, [3, 1, 0, 2])
    
    def test_same_arrival_time(self):
        # All packets arrive at the same time
        arrival_time = [0, 0, 0]
        priority = [5, 10, 1]
        deadline = [10, 12, 8]
        processing_time = [2, 4, 3]
        # Expected ordering is determined by maximizing on-time priority;
        # here the assumed optimal order is to process packet 1 first, then packet 0, then packet 2.
        expected = [1, 0, 2]
        result = schedule_packets(arrival_time, priority, deadline, processing_time)
        self.assertEqual(result, expected)

    def test_deadline_edge(self):
        # Packets have tight deadlines and different arrival times
        arrival_time = [1, 2, 3]
        priority = [10, 20, 15]
        deadline = [6, 7, 8]
        processing_time = [3, 3, 3]
        # One optimal schedule:
        # Packet 1: start at time 2, finish at 5 -> on time (deadline 7)
        # Packet 2: start at time 5, finish at 8 -> on time (deadline 8)
        # Packet 0: start at time 8, finish at 11 -> late (deadline 6)
        expected = [1, 2, 0]
        result = schedule_packets(arrival_time, priority, deadline, processing_time)
        self.assertEqual(result, expected)

    def test_multiple_edge_cases(self):
        # Mixed arrival times and deadlines, some packets can be processed on time while others cannot.
        arrival_time = [0, 2, 4, 6, 8]
        priority = [3, 8, 6, 10, 2]
        deadline = [10, 9, 14, 12, 15]
        processing_time = [3, 2, 4, 1, 5]
        # One candidate schedule:
        # Packet 3: available at 6, processed in 1 time unit, finish at 7 (on time)
        # Packet 1: available at 2, processed in 2 time units, finish at 9 (exactly on time)
        # Packet 2: available at 4, processed in 4 time units, finish at 13 (on time)
        # Packets 0 and 4 will be processed later and miss deadlines.
        expected = [3, 1, 2, 0, 4]
        result = schedule_packets(arrival_time, priority, deadline, processing_time)
        self.assertEqual(result, expected)

    def test_all_packets_missed(self):
        # Scenario where no packet can be processed within its deadline.
        arrival_time = [5, 6, 7]
        priority = [10, 20, 30]
        deadline = [6, 7, 8]
        processing_time = [10, 10, 10]
        # With no possibility to meet a deadline, the schedule might default
        # to processing in the order of arrival.
        expected = [0, 1, 2]
        result = schedule_packets(arrival_time, priority, deadline, processing_time)
        self.assertEqual(result, expected)

    def test_complex_ordering(self):
        # A complex scenario with various arrival times, priorities, deadlines, and processing times.
        arrival_time = [0, 1, 3, 5, 7, 8, 10]
        priority = [5, 15, 10, 30, 20, 25, 5]
        deadline = [12, 12, 15, 18, 20, 22, 25]
        processing_time = [3, 3, 5, 2, 4, 3, 1]
        # One potential optimal schedule:
        # Packet 0: start at 0, finish at 3 -> on time
        # Packet 1: start at 3, finish at 6 -> on time
        # Packet 3: start at max(5,6)=6, finish at 8 -> on time
        # Packet 5: start at max(8,8)=8, finish at 11 -> on time
        # Packet 6: start at max(10,11)=11, finish at 12 -> on time
        # Packet 2: start at max(3,12)=12, finish at 17 -> late (deadline 15)
        # Packet 4: start at max(7,17)=17, finish at 21 -> late (deadline 20)
        expected = [0, 1, 3, 5, 6, 2, 4]
        result = schedule_packets(arrival_time, priority, deadline, processing_time)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()