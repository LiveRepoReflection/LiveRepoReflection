## Project Name

```
Network Congestion Control Simulation
```

## Question Description

You are tasked with simulating a simplified network congestion control algorithm. Imagine a network with a single bottleneck link. Several senders are transmitting data packets through this link to various receivers. The goal is to design an algorithm that allows the senders to dynamically adjust their sending rates to avoid overwhelming the bottleneck link and causing packet loss (congestion).

**Specifics:**

1.  **Network Model:** The network consists of `N` senders and a single bottleneck link with a fixed capacity `C` (packets per second). Each sender `i` has a sending rate `r_i` (packets per second), which they can adjust.

2.  **Congestion Signal:**  A central monitoring entity at the bottleneck link observes the total sending rate `R = sum(r_i)`. If `R > C`, the link is congested. The monitoring entity then sends a congestion notification to a subset of the senders.  The congestion signal includes a parameter `reduction_factor`. Upon receiving the congestion notification, senders MUST reduce their sending rate to `r_i * reduction_factor`.

3.  **Sender Adjustment:** Senders that *do not* receive a congestion notification increase their sending rate slightly to probe the network for available bandwidth. The increase is determined by an additive increase parameter `alpha`. Their new rate becomes `r_i + alpha`.

4.  **Packet Loss Simulation:** If `R > C`, some packets are lost. Simulate packet loss by calculating the packet loss percentage `loss_percentage = (R - C) / R`.

5.  **Fairness:** The algorithm should aim for *max-min fairness*.  This means that no sender can increase its rate without decreasing the rate of another sender that has a smaller rate. This is a challenging aspect to implement in a distributed fashion.

6.  **Constraints:**
    *   The bottleneck link capacity `C` is a positive integer.
    *   The initial sending rate `r_i` for each sender is a positive floating-point number.
    *   The additive increase parameter `alpha` is a positive floating-point number.
    *   The reduction factor is a floating-point number between 0 and 1 (exclusive).
    *   The simulation should run for a fixed number of iterations `T`.
    *   The number of senders `N` can be large (e.g., up to 1000).
    *   **Optimization Requirement:** The simulation must be computationally efficient, especially for large `N` and `T`. Avoid naive implementations that iterate through all senders multiple times per iteration.

**Input:**

*   `N`: The number of senders (integer).
*   `C`: The bottleneck link capacity (integer).
*   `initial_rates`: A list of `N` floating-point numbers, representing the initial sending rates of each sender.
*   `alpha`: The additive increase parameter (float).
*   `reduction_factor`: The reduction factor (float).
*   `T`: The number of simulation iterations (integer).
*   `congestion_notification_probability`: The probability that any given sender will receive a congestion notification (float between 0 and 1 inclusive). The central monitoring entity randomly selects senders to notify based on this probability.

**Output:**

A list of lists. Each inner list represents the sending rates of all `N` senders at a particular iteration. The outer list contains `T` such inner lists, one for each iteration of the simulation.

**Example:**

If `N = 2`, `C = 10`, `initial_rates = [4.0, 5.0]`, `alpha = 0.1`, `reduction_factor = 0.5`, `T = 3`, and `congestion_notification_probability = 0.5`, then the output might look like this (the exact values will vary due to the random nature of congestion notification):

```
[
    [4.0, 5.0],  # Initial rates
    [2.0, 5.1],  # After iteration 1 (sender 1 got notified, sender 2 did not)
    [1.0, 5.2],  # After iteration 2 (sender 1 got notified, sender 2 did not)
    [0.5, 5.3]   # After iteration 3 (sender 1 got notified, sender 2 did not)
]
```

**Challenges:**

*   **Efficiency:**  The naive approach of iterating through all senders in each iteration will be too slow for large `N` and `T`. You need to find a way to optimize the simulation. Consider using vectorized operations with NumPy or other techniques to speed up the calculations.
*   **Fairness:** Achieving max-min fairness in a distributed simulation is difficult. You need to design a strategy that prevents high-rate senders from continuously increasing their rates at the expense of low-rate senders.
*   **Randomness:** The random nature of congestion notification introduces variability in the results. Your algorithm should be robust enough to handle this randomness and still maintain reasonable fairness and stability.
*   **Edge Cases:** Consider edge cases such as:
    *   What happens when initial rates are very low compared to C?
    *   What happens when `alpha` is very large?
    *   What happens when `reduction_factor` is very small?
    *   What happens when `congestion_notification_probability` is 0 or 1?

This problem tests your ability to combine algorithmic thinking, data structure manipulation, and optimization techniques to simulate a complex real-world scenario. Good luck!
