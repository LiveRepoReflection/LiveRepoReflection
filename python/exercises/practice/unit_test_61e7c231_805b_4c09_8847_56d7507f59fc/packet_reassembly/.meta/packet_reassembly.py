from collections import defaultdict
from typing import List, Dict, Optional, Union

def reassemble_file(packets: List[Dict[str, Union[int, str]]]) -> Optional[str]:
    """
    Reassemble a file from network packets.
    
    Args:
        packets: List of dictionaries containing packet information
        
    Returns:
        Reassembled file as string, or None if reassembly is impossible
        
    Raises:
        ValueError: If packets contain inconsistent or invalid data
        KeyError: If packets are missing required fields
    """
    if not packets:
        return None

    # Validate required keys exist in all packets
    required_keys = {'packet_id', 'total_packets', 'packet_index', 'data'}
    for packet in packets:
        if not all(key in packet for key in required_keys):
            raise KeyError("Missing required packet fields")

    # Group packets by packet_id
    packet_groups = defaultdict(list)
    for packet in packets:
        packet_groups[packet['packet_id']].append(packet)

    # Process each group of packets
    for packet_id, group in packet_groups.items():
        # Validate total_packets consistency
        total_packets = group[0]['total_packets']
        if total_packets <= 0:
            raise ValueError("Total packets must be greater than 0")
        
        if any(p['total_packets'] != total_packets for p in group):
            raise ValueError("Inconsistent total_packets values")

        # Validate packet indices
        indices = [p['packet_index'] for p in group]
        if any(idx < 0 or idx >= total_packets for idx in indices):
            raise ValueError("Invalid packet index")
        
        if len(set(indices)) != len(indices):
            raise ValueError("Duplicate packet indices")

        # Check if we have all packets for this file
        if len(group) == total_packets:
            # Sort packets by index and concatenate data
            sorted_packets = sorted(group, key=lambda x: x['packet_index'])
            return ''.join(p['data'] for p in sorted_packets)

    # If we reach here, no complete file was found
    return None