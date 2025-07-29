## Project Name

Network Congestion Control Simulation

## Question Description

You are tasked with simulating a simplified network congestion control algorithm. The goal is to implement a sender that adjusts its sending rate based on feedback from the network, aiming to maximize throughput while avoiding congestion. This simulation will focus on a single sender-receiver pair with a bottleneck link in the network.

**Scenario:**

A sender wants to transmit data packets to a receiver through a network with a bottleneck link. The bottleneck link has a limited capacity. If the sender sends data too quickly, packets will be lost due to congestion at the bottleneck link. The sender uses a congestion control algorithm to adjust its sending rate based on feedback from the network in the form of acknowledgements (ACKs) and packet loss indications.

**Requirements:**

1.  **Implement the following classes:**

    *   `Sender`: Represents the sender side. It should implement:

        *   `__init__(self, initial_rate, max_rate)`: Initializes the sender with an initial sending rate (`initial_rate`) and a maximum sending rate (`max_rate`). The sending rate represents the number of packets the sender attempts to send per time unit.
        *   `send_packets(self, time)`: Simulates sending packets at the current sending rate for a given time unit (`time`). Returns the number of packets sent (which should be the sending rate, rounded down to the nearest integer).
        *   `receive_ack(self)`: Called when the sender receives an ACK. The sender should increase its sending rate according to the congestion control algorithm.
        *   `receive_loss_indication(self)`: Called when the sender receives a packet loss indication. The sender should decrease its sending rate according to the congestion control algorithm.
        *   `get_rate(self)`: Returns the current sending rate.

    *   `BottleneckLink`: Represents the bottleneck link in the network. It should implement:

        *   `__init__(self, capacity, buffer_size)`: Initializes the link with a capacity (`capacity`) representing the maximum number of packets it can transmit per time unit and a buffer size (`buffer_size`) representing the maximum number of packets it can hold.
        *   `transmit(self, packets_sent)`: Simulates transmitting packets through the link. If the number of packets sent (`packets_sent`) exceeds the link's capacity, the excess packets are dropped. If the number of packets sent exceeds buffer size then packets are dropped until the buffer is full. Returns a tuple: (number of packets successfully transmitted, a boolean indicating whether any packets were lost).
        *   `generate_feedback(self, packets_transmitted)`: Simulates generating feedback to the sender. For simplicity, assume that for every `packets_transmitted` packets successfully transmitted, an ACK is generated.  Also, assume that if `packets_sent` > `capacity` then a single loss indication is generated. The feedback mechanism is simplified; a real network would have more complex feedback. Returns a tuple: (number of ACKs, boolean loss_indication).

    *   `Simulator`: Orchestrates the simulation. It should implement:

        *   `__init__(self, sender, bottleneck_link, duration)`: Initializes the simulation with a `sender`, a `bottleneck_link`, and a simulation `duration` (number of time units).
        *   `run(self)`: Runs the simulation for the specified duration. In each time unit:
            1.  The sender sends packets.
            2.  The bottleneck link transmits the packets.
            3.  The bottleneck link generates feedback (ACKs and loss indications).
            4.  The sender processes the feedback to adjust its sending rate.
            Returns a list of the sender's sending rates at each time unit.

2.  **Implement a Congestion Control Algorithm:**

    The sender must implement a congestion control algorithm. You can choose a simplified version of TCP's Additive Increase/Multiplicative Decrease (AIMD) or any other algorithm. Here's a suggested AIMD approach:

    *   **Additive Increase:** Upon receiving an ACK, the sender increases its sending rate by a small amount (e.g., 1 packet per time unit, or a fraction of the current rate).
    *   **Multiplicative Decrease:** Upon receiving a loss indication, the sender decreases its sending rate by a factor (e.g., halves its sending rate).

3.  **Constraints:**

    *   The simulation should be discrete-time.
    *   The sender's sending rate should not exceed `max_rate` and should not be negative.
    *   Prioritize maximizing throughput (number of packets successfully transmitted) while minimizing packet loss.
    *   The `BottleneckLink` should accurately simulate packet loss based on its capacity and buffer size.

4.  **Optimization:**

    *   The simulation should be reasonably efficient. Avoid unnecessary loops or redundant calculations, especially within the simulation's main loop.
    *   Consider using appropriate data structures for efficiently managing packets within the bottleneck link (if you choose to implement a more detailed packet queuing model).

5.  **Edge Cases:**

    *   Handle cases where the initial sending rate is higher than the bottleneck link's capacity.
    *   Handle cases where the sender's sending rate reaches `max_rate`.
    *   Handle cases where there are no packets sent.

**Example Usage:**

```python
initial_rate = 10
max_rate = 100
capacity = 50
buffer_size = 100
duration = 100

sender = Sender(initial_rate, max_rate)
bottleneck_link = BottleneckLink(capacity, buffer_size)
simulator = Simulator(sender, bottleneck_link, duration)

rates = simulator.run()
print(rates) # Output: A list of sending rates at each time unit.
```

**Grading:**

*   Correctness: The code should accurately simulate the network and the chosen congestion control algorithm.
*   Efficiency: The code should be reasonably efficient, avoiding unnecessary computations.
*   Robustness: The code should handle edge cases and invalid inputs gracefully.
*   Clarity: The code should be well-structured and easy to understand, with appropriate comments.

This problem requires a combination of algorithmic thinking, system design, and attention to detail. Good luck!
