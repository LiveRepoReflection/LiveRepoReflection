# Distributed Data Aggregation - Median Calculation

This project implements a distributed system for real-time calculation of the median across a network of sensors. The system is designed to be efficient, scalable, and fault-tolerant.

## System Architecture

The system consists of three main components:

1. **Sensor Nodes**: Generate numerical data and send it to their assigned aggregation server.
2. **Aggregation Servers**: Collect data from multiple sensor nodes and prepare it for central processing.
3. **Central Server**: Aggregates data from all servers to calculate the global median.

## Key Features

- **Scalability**: Can handle a large number of sensors and aggregation servers.
- **Bandwidth Efficiency**: Uses data sketches to minimize communication overhead.
- **Fault Tolerance**: Can handle failure of individual sensor nodes.
- **Real-Time Processing**: Provides up-to-date median estimates with minimal latency.

## Implementation Details

### Data Structures

- **MedianSketch**: A probabilistic data structure that provides an approximation of the median while using constant memory.
- **Heaps**: Used for exact median calculation in smaller datasets.

### Algorithms

- **Exact Median Calculation**: For small datasets, we calculate the exact median by collecting all values.
- **Approximate Median**: For large datasets, we use a quantile sketch approach.
- **Merge Operation**: Efficiently combines sketches from multiple aggregation servers.

## Trade-offs

This implementation balances several competing concerns:

- **Accuracy vs. Bandwidth**: More accurate median calculations require more data transmission.
- **Timeliness vs. Completeness**: Waiting for all sensors to report increases latency.
- **Memory Usage vs. Precision**: More precise sketches require more memory.

## Running the Simulation

To run a simulation of the system:
