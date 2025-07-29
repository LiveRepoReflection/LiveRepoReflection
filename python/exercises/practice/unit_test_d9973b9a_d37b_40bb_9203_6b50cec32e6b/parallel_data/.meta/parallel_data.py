import math
import multiprocessing as mp
from itertools import islice
from collections import OrderedDict

def filter_records(record):
    """Filter records where status is 'active'."""
    return record.get("status") == "active"

def map_records(record):
    """Add processed_value field as square root of absolute value."""
    # Get the value, handle various types and edge cases
    value = record.get("value", 0)
    
    try:
        if value is None:
            processed_value = 0.0
        else:
            # Try to convert to float if it's a string
            if isinstance(value, str):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    value = 0.0
            
            # Handle non-numeric types
            if not isinstance(value, (int, float)):
                processed_value = 0.0
            else:
                # Handle NaN and infinity
                if math.isnan(value) or math.isinf(value):
                    processed_value = 0.0
                else:
                    # Calculate square root of absolute value
                    processed_value = math.sqrt(abs(value))
    except Exception:
        # Catch any unexpected errors and default to 0.0
        processed_value = 0.0
    
    # Create a new record with processed_value
    record["processed_value"] = processed_value
    return record

def chunk_generator(data_source, chunk_size):
    """Split a generator into chunks of specified size."""
    while True:
        chunk = list(islice(data_source, chunk_size))
        if not chunk:
            break
        yield chunk

def worker_process(chunk):
    """Process a chunk of data through filtering and mapping."""
    # Filter active records
    filtered = filter(filter_records, chunk)
    # Map to add processed_value
    mapped = map(map_records, filtered)
    return list(mapped)

def deduplicate_records(records):
    """Remove duplicates based on user_id and processed_value."""
    seen = set()
    unique_records = []
    
    for record in records:
        # Skip records without user_id
        if "user_id" not in record or "processed_value" not in record:
            continue
            
        # Create a key based on user_id and processed_value
        key = (record["user_id"], record["processed_value"])
        
        # If we haven't seen this key before, add it to our result
        if key not in seen:
            seen.add(key)
            unique_records.append(record)
            
    return unique_records

def calculate_average(records):
    """Calculate the average processed_value."""
    if not records:
        return 0.0
        
    total = sum(record["processed_value"] for record in records)
    return total / len(records)

def process_data(data_source, num_processes, max_records=None):
    """
    Process data in parallel using multiple processes.
    
    Args:
        data_source: An iterable that yields dictionaries.
        num_processes: Number of processes to use for parallel processing.
        max_records: Optional limit on the number of records to process (for testing).
        
    Returns:
        Average of processed_value after filtering, mapping, and deduplication.
    """
    # Validate num_processes
    if not isinstance(num_processes, int) or num_processes <= 0:
        raise ValueError("num_processes must be a positive integer")
    
    # Limit the number of records for testing purposes
    if max_records is not None:
        data_source = islice(data_source, max_records)
    
    # Determine chunk size based on number of processes
    chunk_size = max(10, 1000 // num_processes)  # Adjust based on expected data size
    
    # Collection for all processed records
    all_processed_records = []
    
    # Use process pool to process data in parallel
    with mp.Pool(processes=num_processes) as pool:
        # Process chunks of data in parallel
        for chunk in chunk_generator(data_source, chunk_size):
            # Process multiple chunks in parallel
            processed_chunk = pool.apply(worker_process, (chunk,))
            all_processed_records.extend(processed_chunk)
    
    # Deduplicate records
    unique_records = deduplicate_records(all_processed_records)
    
    # Calculate average
    return calculate_average(unique_records)