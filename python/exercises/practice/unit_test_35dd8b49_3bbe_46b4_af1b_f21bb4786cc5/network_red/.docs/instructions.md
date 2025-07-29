## Project Name

```
Network Congestion Avoidance
```

## Question Description

You are designing a network router that must implement a sophisticated congestion avoidance mechanism. The router handles packets arriving from various sources and destined for different outputs. Due to network limitations, each output has a maximum bandwidth capacity. Your task is to simulate the router's packet processing under a specific congestion avoidance strategy.

**Input:**

You are given a list of packets. Each packet is represented by a tuple: `(arrival_time, output_port, packet_size)`.

*   `arrival_time`: An integer representing the time the packet arrives at the router (non-negative).
*   `output_port`: An integer representing the destination output port of the packet (0-indexed).
*   `packet_size`: An integer representing the size of the packet in bytes.

You are also given the following:

*   `num_outputs`: An integer representing the total number of output ports on the router.
*   `bandwidth_capacities`: A list of integers representing the bandwidth capacity (in bytes per unit time) for each output port. `bandwidth_capacities[i]` is the capacity of output port `i`.
*   `queue_size_limit`: An integer specifying the maximum number of packets each output queue can hold. Once an output queue reaches its limit, any further incoming packets destined for that output will be dropped.
*   `red_parameters`: A dictionary containing RED (Random Early Detection) parameters:
    *   `min_threshold`: Minimum queue size threshold before RED starts dropping packets.
    *   `max_threshold`: Maximum queue size threshold; when the queue size exceeds this, all incoming packets are dropped.
    *   `max_p`: Maximum probability of dropping a packet when the queue size is between `min_threshold` and `max_threshold`.

**Congestion Avoidance Strategy (RED):**

Implement the RED (Random Early Detection) algorithm for congestion avoidance.

1.  **Queue Management:** Each output port has its own queue to hold packets waiting to be transmitted.
2.  **Packet Dropping:** When a packet arrives at an output queue:
    *   If the queue is full (reached `queue_size_limit`), drop the packet.
    *   Otherwise, calculate the average queue size.
    *   If the average queue size is less than `min_threshold`, accept the packet into the queue.
    *   If the average queue size is greater than or equal to `max_threshold`, drop the packet.
    *   If the average queue size is between `min_threshold` and `max_threshold`, calculate a probability `p` based on the following formula:

        `p = max_p * (avg_queue_size - min_threshold) / (max_threshold - min_threshold)`

        Generate a random number between 0 and 1. If the random number is less than `p`, drop the packet. Otherwise, accept the packet into the queue.
3.  **Packet Transmission:** At each unit of time, each output port transmits as many bytes as its bandwidth capacity allows, processing packets in FIFO (First-In-First-Out) order. If a packet's size exceeds the remaining bandwidth, only a portion of the packet is transmitted, and the remaining portion is transmitted in subsequent time units.
4.  **Average Queue Size:** Calculate the average queue size using Exponential Weighted Moving Average (EWMA) with a weight `w = 0.2`.

    `avg_queue_size = (1 - w) * avg_queue_size + w * current_queue_size`

    The initial `avg_queue_size` for each queue is 0.

**Output:**

Return a tuple containing the following:

*   `packets_transmitted`: A list of tuples, where each tuple represents a transmitted packet and contains the `arrival_time`, `output_port`, and `packet_size` of the transmitted packet. Order should be the order the packets are fully transmitted.
*   `packets_dropped`: A list of tuples, where each tuple represents a dropped packet and contains the `arrival_time`, `output_port`, and `packet_size` of the dropped packet. Order should be the order the packets are dropped.
*   `final_queue_states`: A list of lists, where each inner list represents the remaining packets (represented by their `packet_size`) in each output queue at the end of the simulation.  `final_queue_states[i]` is the state of the queue for output port `i`.

**Constraints:**

*   All input values are non-negative integers.
*   `1 <= num_outputs <= 100`
*   `1 <= bandwidth_capacities[i] <= 1000`
*   `1 <= queue_size_limit <= 1000`
*   `0 <= min_threshold < max_threshold <= queue_size_limit`
*   `0 < max_p <= 1`
*   The simulation should run until all packets have been either transmitted or dropped, and all queues are empty.
*   Assume time starts at 0.

**Example:**

Let's say you have two output ports, each with a bandwidth of 10 bytes/time unit.  You have a few packets arriving at different times for these output ports.  The RED parameters control how packets are dropped when the queues get congested.  Your code needs to simulate this and return which packets were sent, which were dropped, and what's left in the queues at the end.

**Optimization Requirements:**

*   The solution should be efficient in terms of time complexity. Aim for a solution that avoids unnecessary iterations or redundant calculations.
*   Consider using appropriate data structures to optimize queue operations and packet processing.

This problem requires a good understanding of queuing theory, congestion control algorithms, and the ability to simulate a complex system with multiple interacting components. Good luck!
