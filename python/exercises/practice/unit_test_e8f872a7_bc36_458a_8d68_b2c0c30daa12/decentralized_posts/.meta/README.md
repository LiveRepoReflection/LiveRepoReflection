# Decentralized Posts

This module implements a simulation of a decentralized social network post storage and retrieval system. The system uses a Distributed Hash Table (DHT) approach for content addressing and storage of user posts.

## Features

- Content addressing using SHA-256 hashing
- Distributed post storage across simulated nodes
- K-replication for post redundancy
- Efficient post retrieval by user
- XOR distance-based node proximity calculation

## Core Functions

- `store_post(node_id, user_id, timestamp, content)`: Stores a post in the distributed network
- `retrieve_posts(node_id, user_id)`: Retrieves all posts by a user, sorted by timestamp

## Implementation Details

- The module simulates a DHT network with nodes identified by IDs in range [0, 2^20 - 1]
- Posts are stored on K closest nodes to their Content ID (CID)
- XOR distance is used to calculate proximity between nodes
- Secondary indexing is implemented for efficient retrieval

## Limitations

- This is a simulation and does not implement actual network communication
- The implementation uses in-memory data structures rather than persistent storage
- The node discovery is simplified compared to real DHT implementations