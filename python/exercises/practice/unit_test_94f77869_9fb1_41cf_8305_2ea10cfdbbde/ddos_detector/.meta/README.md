# DDoS Detector

This package implements a real-time network anomaly detection system that identifies potential Distributed Denial-of-Service (DDoS) attacks targeting specific destination IPs.

## Features

- Real-time processing of network packet streams
- Sliding time window analysis
- Anomaly score calculation based on distinct source IPs
- Time decay mechanism for packet influence
- Memory-efficient implementation using approximate data structures

## Usage

The detector reads packets from standard input, with each line containing a JSON representation of a packet:
