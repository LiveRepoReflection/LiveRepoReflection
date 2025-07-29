# Network Packet Analyzer

This package provides an advanced network packet analyzer that can efficiently process and analyze a large stream of network packets in real-time. It identifies and flags potentially malicious or anomalous network activity based on a combination of packet characteristics and pre-defined rules.

## Features

The analyzer implements the following detection rules:

1. **Blacklisted IPs:** Detects traffic from or to blacklisted IP addresses
2. **Port Scanning:** Detects potential port scanning activity
3. **Large Packet Size:** Flags packets exceeding a size threshold
4. **SYN Flood Detection:** Detects potential SYN flood attacks
5. **Unusual Protocol/Port Combinations:** Flags packets using unusual protocol/port combinations

## Usage
