import math

class Sender:
    def __init__(self, initial_rate, max_rate):
        self.current_rate = initial_rate
        self.max_rate = max_rate
        self.min_rate = 0
        self.additive_increase = 1.0
        self.multiplicative_decrease = 0.5

    def send_packets(self, time):
        # Round down to nearest integer for packet count
        return math.floor(self.current_rate)

    def receive_ack(self):
        # Additive Increase
        self.current_rate = min(
            self.max_rate,
            self.current_rate + self.additive_increase
        )

    def receive_loss_indication(self):
        # Multiplicative Decrease
        self.current_rate = max(
            self.min_rate,
            self.current_rate * self.multiplicative_decrease
        )

    def get_rate(self):
        return self.current_rate


class BottleneckLink:
    def __init__(self, capacity, buffer_size):
        self.capacity = capacity
        self.buffer_size = buffer_size

    def transmit(self, packets_sent):
        # First check buffer constraint
        packets_in_buffer = min(packets_sent, self.buffer_size)
        
        # Then check capacity constraint
        packets_transmitted = min(packets_in_buffer, self.capacity)
        
        # Determine if there was packet loss
        packets_lost = packets_sent > packets_transmitted
        
        return packets_transmitted, packets_lost

    def generate_feedback(self, packets_transmitted):
        # Generate one ACK for each successfully transmitted packet
        acks = packets_transmitted
        
        # Generate loss indication if transmitted packets hit capacity
        loss_indication = packets_transmitted >= self.capacity
        
        return acks, loss_indication


class Simulator:
    def __init__(self, sender, bottleneck_link, duration):
        self.sender = sender
        self.bottleneck_link = bottleneck_link
        self.duration = duration

    def run(self):
        rates = []
        
        for _ in range(self.duration):
            # Record current rate
            current_rate = self.sender.get_rate()
            rates.append(current_rate)
            
            # Sender sends packets
            packets_sent = self.sender.send_packets(1)
            
            # Packets go through bottleneck link
            packets_transmitted, packets_lost = self.bottleneck_link.transmit(packets_sent)
            
            # Generate feedback
            acks, loss_indication = self.bottleneck_link.generate_feedback(packets_transmitted)
            
            # Process feedback
            for _ in range(acks):
                self.sender.receive_ack()
                
            if loss_indication:
                self.sender.receive_loss_indication()
        
        return rates


if __name__ == "__main__":
    # Example usage
    initial_rate = 10
    max_rate = 100
    capacity = 50
    buffer_size = 100
    duration = 100

    sender = Sender(initial_rate, max_rate)
    bottleneck_link = BottleneckLink(capacity, buffer_size)
    simulator = Simulator(sender, bottleneck_link, duration)

    rates = simulator.run()
    print("Sending rates over time:", rates)