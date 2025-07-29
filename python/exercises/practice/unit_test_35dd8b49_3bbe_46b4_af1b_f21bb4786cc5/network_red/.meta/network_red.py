import heapq
import random
from collections import deque

class OutputQueue:
    def __init__(self, bandwidth_capacity, queue_size_limit, red_parameters):
        self.bandwidth_capacity = bandwidth_capacity
        self.queue_size_limit = queue_size_limit
        self.red_parameters = red_parameters
        self.queue = deque()
        self.avg_queue_size = 0
        self.current_packet = None
        self.remaining_bytes = 0
        self.weight = 0.2  # EWMA weight

    def update_avg_queue_size(self):
        current_size = len(self.queue)
        self.avg_queue_size = (1 - self.weight) * self.avg_queue_size + self.weight * current_size

    def should_drop_packet(self):
        if len(self.queue) >= self.queue_size_limit:
            return True

        self.update_avg_queue_size()
        
        if self.avg_queue_size < self.red_parameters['min_threshold']:
            return False
        
        if self.avg_queue_size >= self.red_parameters['max_threshold']:
            return True

        # Calculate drop probability
        drop_prob = (self.red_parameters['max_p'] * 
                    (self.avg_queue_size - self.red_parameters['min_threshold']) /
                    (self.red_parameters['max_threshold'] - self.red_parameters['min_threshold']))
        
        return random.random() < drop_prob

    def add_packet(self, packet):
        if self.should_drop_packet():
            return False
        self.queue.append(packet)
        return True

    def process_time_unit(self, current_time):
        transmitted_packets = []
        bytes_remaining = self.bandwidth_capacity

        # Continue processing current packet if any
        if self.current_packet and self.remaining_bytes > 0:
            bytes_transmitted = min(bytes_remaining, self.remaining_bytes)
            self.remaining_bytes -= bytes_transmitted
            bytes_remaining -= bytes_transmitted

            if self.remaining_bytes == 0:
                transmitted_packets.append(self.current_packet)
                self.current_packet = None

        # Process new packets
        while bytes_remaining > 0 and self.queue:
            if not self.current_packet:
                self.current_packet = self.queue.popleft()
                self.remaining_bytes = self.current_packet[2]  # packet_size

            bytes_transmitted = min(bytes_remaining, self.remaining_bytes)
            self.remaining_bytes -= bytes_transmitted
            bytes_remaining -= bytes_transmitted

            if self.remaining_bytes == 0:
                transmitted_packets.append(self.current_packet)
                self.current_packet = None

        return transmitted_packets

def process_packets(packets, num_outputs, bandwidth_capacities, queue_size_limit, red_parameters):
    if not (1 <= num_outputs <= 100):
        raise ValueError("Number of outputs must be between 1 and 100")

    if not all(1 <= bw <= 1000 for bw in bandwidth_capacities):
        raise ValueError("Bandwidth capacities must be between 1 and 1000")

    if not (1 <= queue_size_limit <= 1000):
        raise ValueError("Queue size limit must be between 1 and 1000")

    # Initialize output queues
    output_queues = [OutputQueue(bandwidth_capacities[i], queue_size_limit, red_parameters) 
                    for i in range(num_outputs)]
    
    # Sort packets by arrival time
    sorted_packets = sorted(packets, key=lambda x: x[0])
    
    current_time = 0
    packet_index = 0
    transmitted_packets = []
    dropped_packets = []
    
    # Process packets until all are handled and queues are empty
    while packet_index < len(sorted_packets) or any(len(q.queue) > 0 or q.current_packet 
                                                  for q in output_queues):
        # Add new packets that have arrived
        while packet_index < len(sorted_packets) and sorted_packets[packet_index][0] <= current_time:
            packet = sorted_packets[packet_index]
            if packet[1] >= num_outputs:
                raise ValueError(f"Invalid output port: {packet[1]}")
                
            if not output_queues[packet[1]].add_packet(packet):
                dropped_packets.append(packet)
            packet_index += 1
        
        # Process packets in each output queue
        for queue in output_queues:
            transmitted = queue.process_time_unit(current_time)
            transmitted_packets.extend(transmitted)
        
        current_time += 1
    
    # Prepare final queue states
    final_queue_states = [list(q.queue) for q in output_queues]
    
    return transmitted_packets, dropped_packets, [[p[2] for p in q] for q in final_queue_states]