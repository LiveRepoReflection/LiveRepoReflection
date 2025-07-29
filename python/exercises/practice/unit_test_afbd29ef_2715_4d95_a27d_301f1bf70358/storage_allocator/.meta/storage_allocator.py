import heapq
from collections import defaultdict
from typing import List, Tuple, Dict, Set, Any


def optimize_storage_allocation(
    devices: List[Tuple[str, int, Set[str]]],
    chunks: List[Tuple[str, int, Set[str]]]
) -> Dict[str, List[str]]:
    """
    Optimally allocate data chunks to storage devices based on capacity and capability requirements.
    
    Args:
        devices: List of tuples (device_id, capacity, capabilities) representing storage devices
        chunks: List of tuples (chunk_id, size, required_capabilities) representing data chunks
        
    Returns:
        A dictionary mapping device_id to a list of allocated chunk_ids.
        Unallocated chunks are mapped to the key "unallocated".
    """
    # Validate input
    _validate_input(devices, chunks)
    
    if not chunks:
        return {}
        
    if not devices:
        return {"unallocated": [chunk[0] for chunk in chunks]}
    
    # Preprocess: Index devices by capabilities
    devices_by_capability = _index_devices_by_capability(devices)
    
    # Sort chunks by size (descending) to allocate larger chunks first
    # This is a common heuristic for bin packing problems
    sorted_chunks = sorted(chunks, key=lambda x: x[1], reverse=True)
    
    # Try to allocate chunks using different strategies
    return _allocate_chunks_with_bin_packing(devices, sorted_chunks, devices_by_capability)


def _validate_input(
    devices: List[Tuple[str, int, Set[str]]],
    chunks: List[Tuple[str, int, Set[str]]]
) -> None:
    """Validate the input format for devices and chunks."""
    for device_id, capacity, capabilities in devices:
        if not isinstance(capacity, int):
            raise TypeError(f"Device {device_id} capacity must be an integer")
        if not isinstance(capabilities, set):
            raise TypeError(f"Device {device_id} capabilities must be a set")
            
    for chunk_id, size, required_capabilities in chunks:
        if not isinstance(size, int):
            raise TypeError(f"Chunk {chunk_id} size must be an integer")
        if not isinstance(required_capabilities, set):
            raise TypeError(f"Chunk {chunk_id} required capabilities must be a set")


def _index_devices_by_capability(
    devices: List[Tuple[str, int, Set[str]]]
) -> Dict[str, List[Tuple[str, int, Set[str]]]]:
    """
    Index devices by their supported capabilities for faster lookup.
    
    Args:
        devices: List of (device_id, capacity, capabilities) tuples
        
    Returns:
        Dictionary mapping each capability to a list of devices supporting it
    """
    devices_by_capability = defaultdict(list)
    
    for device in devices:
        device_id, capacity, capabilities = device
        for capability in capabilities:
            devices_by_capability[capability].append(device)
            
    return devices_by_capability


def _find_compatible_devices(
    chunk: Tuple[str, int, Set[str]],
    devices_by_capability: Dict[str, List[Tuple[str, int, Set[str]]]]
) -> Set[str]:
    """
    Find all devices that are compatible with a given chunk's requirements.
    
    Args:
        chunk: Tuple of (chunk_id, size, required_capabilities)
        devices_by_capability: Dictionary mapping capabilities to devices
        
    Returns:
        Set of device_ids compatible with the chunk
    """
    chunk_id, chunk_size, required_capabilities = chunk
    
    # If no requirements, all devices are compatible
    if not required_capabilities:
        return {device[0] for capability in devices_by_capability for device in devices_by_capability[capability]}
    
    # Start with all devices supporting the first capability
    if not required_capabilities or next(iter(required_capabilities)) not in devices_by_capability:
        return set()
        
    compatible_devices = {device[0] for device in devices_by_capability[next(iter(required_capabilities))]}
    
    # Intersect with devices supporting each other required capability
    for capability in required_capabilities:
        if capability not in devices_by_capability:
            return set()  # No devices support this capability
            
        compatible_devices &= {device[0] for device in devices_by_capability[capability]}
        
    return compatible_devices


def _allocate_chunks_with_bin_packing(
    devices: List[Tuple[str, int, Set[str]]],
    chunks: List[Tuple[str, int, Set[str]]],
    devices_by_capability: Dict[str, List[Tuple[str, int, Set[str]]]]
) -> Dict[str, List[str]]:
    """
    Allocate chunks to devices using a bin packing strategy.
    
    This function uses the First-Fit Decreasing algorithm, which is a common
    heuristic for bin packing problems. Chunks are sorted by size (descending)
    and each chunk is placed in the first device that can accommodate it.
    
    Args:
        devices: List of (device_id, capacity, capabilities) tuples
        chunks: List of (chunk_id, size, required_capabilities) tuples, sorted by size
        devices_by_capability: Dictionary mapping capabilities to devices
        
    Returns:
        Dictionary mapping device_id to list of allocated chunk_ids
    """
    # Create a mapping from device_id to device for O(1) lookup
    device_map = {device[0]: device for device in devices}
    
    # Initialize remaining capacity for each device
    remaining_capacity = {device[0]: device[1] for device in devices}
    
    # Initialize allocation dictionary
    allocation = defaultdict(list)
    
    # Track devices in use (to minimize the number of devices used)
    devices_in_use = set()
    
    # Process each chunk in order of size (largest first)
    for chunk in chunks:
        chunk_id, chunk_size, required_capabilities = chunk
        
        # Find compatible devices
        compatible_device_ids = _find_compatible_devices(chunk, devices_by_capability)
        
        # Filter to only include devices with sufficient capacity
        viable_devices = [(device_id, remaining_capacity[device_id]) 
                         for device_id in compatible_device_ids 
                         if remaining_capacity[device_id] >= chunk_size]
        
        if not viable_devices:
            # No viable device found, add to unallocated
            allocation["unallocated"].append(chunk_id)
            continue
            
        # Strategy 1: Prefer devices already in use to minimize total devices used
        used_devices = [(device_id, capacity) for device_id, capacity in viable_devices if device_id in devices_in_use]
        
        if used_devices:
            # Use best-fit strategy for devices already in use
            target_device_id = min(used_devices, key=lambda x: x[1] - chunk_size)[0]
        else:
            # If no device is in use yet or no used device can accommodate the chunk,
            # use the device with largest capacity (to maximize the chance of fitting more chunks)
            target_device_id = max(viable_devices, key=lambda x: x[1])[0]
            devices_in_use.add(target_device_id)
        
        # Allocate the chunk
        allocation[target_device_id].append(chunk_id)
        remaining_capacity[target_device_id] -= chunk_size
    
    # Clean up empty entries in the allocation dictionary
    result = {k: v for k, v in allocation.items() if v}
    
    return result


def _allocate_chunks_with_max_flow(
    devices: List[Tuple[str, int, Set[str]]],
    chunks: List[Tuple[str, int, Set[str]]],
    devices_by_capability: Dict[str, List[Tuple[str, int, Set[str]]]]
) -> Dict[str, List[str]]:
    """
    Alternative allocation algorithm using a greedy approach with a graph-based model.
    
    This approach tries to model the allocation problem as a bipartite graph matching problem,
    where chunks are connected to compatible devices. We then greedily assign chunks to devices
    based on multiple criteria.
    
    Args:
        devices: List of (device_id, capacity, capabilities) tuples
        chunks: List of (chunk_id, size, required_capabilities) tuples
        devices_by_capability: Dictionary mapping capabilities to devices
        
    Returns:
        Dictionary mapping device_id to list of allocated chunk_ids
    """
    # Create a mapping from device_id to device for O(1) lookup
    device_map = {device[0]: device for device in devices}
    
    # Initialize remaining capacity for each device
    remaining_capacity = {device[0]: device[1] for device in devices}
    
    # Initialize allocation dictionary
    allocation = defaultdict(list)
    
    # Precompute compatibility matrix: chunk_id -> list of compatible devices
    compatibility = {}
    for chunk in chunks:
        chunk_id, chunk_size, required_capabilities = chunk
        compatible_device_ids = _find_compatible_devices(chunk, devices_by_capability)
        compatibility[chunk_id] = compatible_device_ids
    
    # Group chunks by the number of compatible devices they have (prioritize chunks with fewer options)
    chunks_by_options = defaultdict(list)
    for chunk in chunks:
        chunk_id = chunk[0]
        num_options = len(compatibility[chunk_id])
        if num_options > 0:  # Only consider chunks with at least one compatible device
            chunks_by_options[num_options].append(chunk)
    
    # Process chunks in order of increasing number of options
    for num_options in sorted(chunks_by_options.keys()):
        # For chunks with same number of options, process larger chunks first
        for chunk in sorted(chunks_by_options[num_options], key=lambda x: x[1], reverse=True):
            chunk_id, chunk_size, required_capabilities = chunk
            
            # Find devices that can fit this chunk
            viable_devices = []
            for device_id in compatibility[chunk_id]:
                if remaining_capacity[device_id] >= chunk_size:
                    # Calculate how well this device fits the chunk (lower is better)
                    fit_score = remaining_capacity[device_id] - chunk_size
                    viable_devices.append((device_id, fit_score))
            
            if not viable_devices:
                allocation["unallocated"].append(chunk_id)
                continue
                
            # Use best-fit strategy: device with smallest capacity that can fit the chunk
            best_device_id = min(viable_devices, key=lambda x: x[1])[0]
            
            # Allocate the chunk
            allocation[best_device_id].append(chunk_id)
            remaining_capacity[best_device_id] -= chunk_size
    
    # Add remaining chunks to unallocated
    for chunk in chunks:
        chunk_id = chunk[0]
        if not any(chunk_id in allocated_chunks for allocated_chunks in allocation.values()):
            allocation["unallocated"].append(chunk_id)
    
    # Clean up empty entries in the allocation dictionary
    result = {k: v for k, v in allocation.items() if v}
    
    return result