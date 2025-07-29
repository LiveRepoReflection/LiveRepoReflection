from collections import defaultdict, deque
from typing import List, Tuple, Set, Dict, Any


class PacketAnalyzer:
    """
    Advanced Network Packet Analyzer that processes and analyzes network packets
    for detecting various security threats and anomalies.
    """

    def __init__(
        self,
        port_scan_threshold: int = 10,
        time_window_ms: int = 60000,
        large_packet_size: int = 1500,
        syn_flood_threshold: int = 5,
        blacklist: List[str] = None,
        normal_combinations: List[Tuple[str, int]] = None,
    ):
        """
        Initialize the PacketAnalyzer with configurable parameters.

        Args:
            port_scan_threshold: Number of distinct ports to trigger port scanning detection
            time_window_ms: Time window for sliding window rules in milliseconds
            large_packet_size: Threshold for large packet size detection
            syn_flood_threshold: Number of SYN packets to trigger SYN flood detection
            blacklist: List of blacklisted IP addresses
            normal_combinations: List of normal protocol-port combinations
        """
        # Configuration parameters
        self.port_scan_threshold = port_scan_threshold
        self.time_window_ms = time_window_ms
        self.large_packet_size = large_packet_size
        self.syn_flood_threshold = syn_flood_threshold
        self.blacklist = set(blacklist or [])
        self.normal_combinations = set(normal_combinations or [])

        # Data structures for rule processing
        # Dictionary mapping source IPs to dictionaries mapping timestamps to sets of destination ports
        self._port_scan_records: Dict[str, Dict[int, Set[int]]] = defaultdict(dict)
        
        # Dictionary mapping destination IPs to dictionaries mapping timestamps to SYN packet counts
        self._syn_flood_records: Dict[str, Dict[int, int]] = defaultdict(dict)
        
        # List to store flagged packets
        self._flagged_packets: List[str] = []

    def process_packet(self, packet_str: str) -> None:
        """
        Process a single packet and apply all rules.

        Args:
            packet_str: String representation of the packet
        """
        # Parse packet
        (
            timestamp_str,
            source_ip,
            destination_ip,
            source_port_str,
            destination_port_str,
            protocol,
            packet_size_str,
            flags,
        ) = packet_str.split(",")

        # Convert fields to appropriate types
        timestamp = int(timestamp_str)
        source_port = int(source_port_str)
        destination_port = int(destination_port_str)
        packet_size = int(packet_size_str)

        # Apply each rule and flag if violated
        if self._check_blacklisted(source_ip, destination_ip):
            self._flag_packet("BLACKLIST", packet_str)

        if self._check_port_scanning(source_ip, destination_port, timestamp):
            self._flag_packet("PORTSCAN", packet_str)

        if self._check_large_packet(packet_size):
            self._flag_packet("LARGESIZE", packet_str)

        if flags == "SYN" and self._check_syn_flood(destination_ip, timestamp):
            self._flag_packet("SYNFLOOD", packet_str)

        if self._check_unusual_protocol_port(protocol, destination_port):
            self._flag_packet("UNUSUAL", packet_str)

        # Clean up old data to maintain memory efficiency
        self._cleanup_old_data(timestamp)

    def get_flagged_packets(self) -> List[str]:
        """
        Return all flagged packets.

        Returns:
            List of strings, each representing a flagged packet
        """
        return self._flagged_packets

    def _flag_packet(self, reason: str, packet_str: str) -> None:
        """
        Add a packet to the flagged packets list with its reason.

        Args:
            reason: The reason for flagging
            packet_str: The original packet string
        """
        self._flagged_packets.append(f"{reason}:{packet_str}")

    def _check_blacklisted(self, source_ip: str, destination_ip: str) -> bool:
        """
        Check if either source_ip or destination_ip is in the blacklist.

        Args:
            source_ip: Source IP address
            destination_ip: Destination IP address

        Returns:
            True if either IP is blacklisted, False otherwise
        """
        return source_ip in self.blacklist or destination_ip in self.blacklist

    def _check_port_scanning(self, source_ip: str, destination_port: int, timestamp: int) -> bool:
        """
        Check if the source IP is performing a port scan.

        Args:
            source_ip: Source IP address
            destination_port: Destination port
            timestamp: Packet timestamp

        Returns:
            True if port scanning is detected, False otherwise
        """
        # Remove expired data
        records = self._port_scan_records[source_ip]
        
        # Add current port to set for current timestamp
        if timestamp not in records:
            records[timestamp] = set()
        records[timestamp].add(destination_port)
        
        # Count unique ports within time window
        unique_ports = set()
        min_timestamp = timestamp - self.time_window_ms
        
        for ts, ports in list(records.items()):
            if ts >= min_timestamp:
                unique_ports.update(ports)
            else:
                # Cleanup expired timestamps
                del records[ts]
        
        return len(unique_ports) > self.port_scan_threshold

    def _check_large_packet(self, packet_size: int) -> bool:
        """
        Check if the packet size exceeds the large packet size threshold.

        Args:
            packet_size: Size of the packet in bytes

        Returns:
            True if packet is too large, False otherwise
        """
        return packet_size > self.large_packet_size

    def _check_syn_flood(self, destination_ip: str, timestamp: int) -> bool:
        """
        Check if the destination IP is experiencing a SYN flood.

        Args:
            destination_ip: Destination IP address
            timestamp: Packet timestamp

        Returns:
            True if SYN flood is detected, False otherwise
        """
        # Get records for this destination IP
        records = self._syn_flood_records[destination_ip]
        
        # Increment SYN count for current timestamp
        records[timestamp] = records.get(timestamp, 0) + 1
        
        # Count total SYN packets within time window
        syn_count = 0
        min_timestamp = timestamp - self.time_window_ms
        
        for ts, count in list(records.items()):
            if ts >= min_timestamp:
                syn_count += count
            else:
                # Cleanup expired timestamps
                del records[ts]
        
        return syn_count > self.syn_flood_threshold

    def _check_unusual_protocol_port(self, protocol: str, destination_port: int) -> bool:
        """
        Check if the protocol-port combination is unusual.

        Args:
            protocol: Network protocol
            destination_port: Destination port

        Returns:
            True if combination is unusual, False otherwise
        """
        return (protocol, destination_port) not in self.normal_combinations

    def _cleanup_old_data(self, current_timestamp: int) -> None:
        """
        Remove data older than the time window to maintain memory efficiency.

        Args:
            current_timestamp: Current packet timestamp
        """
        min_timestamp = current_timestamp - self.time_window_ms
        
        # Clean up port scan records
        for source_ip in list(self._port_scan_records.keys()):
            records = self._port_scan_records[source_ip]
            for ts in list(records.keys()):
                if ts < min_timestamp:
                    del records[ts]
            if not records:
                del self._port_scan_records[source_ip]
        
        # Clean up SYN flood records
        for dest_ip in list(self._syn_flood_records.keys()):
            records = self._syn_flood_records[dest_ip]
            for ts in list(records.keys()):
                if ts < min_timestamp:
                    del records[ts]
            if not records:
                del self._syn_flood_records[dest_ip]