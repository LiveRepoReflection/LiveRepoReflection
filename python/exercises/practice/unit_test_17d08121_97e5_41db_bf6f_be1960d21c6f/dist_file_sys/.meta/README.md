# Distributed File System

This package implements a simple distributed file system with the following components:

- **Storage Nodes**: Responsible for storing file chunks
- **Metadata Server**: Manages file metadata and chunk locations
- **Distributed File System**: Coordinates the nodes for file operations

## Features

- File chunking and distribution
- Replication for fault tolerance
- Round-robin chunk distribution
- Concurrent read and write operations
- Graceful handling of node failures

## Usage Example
