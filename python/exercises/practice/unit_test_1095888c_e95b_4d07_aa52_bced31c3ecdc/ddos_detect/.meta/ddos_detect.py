from collections import deque

def detect_ddos(flow_records, time_window, threshold_factor, min_source_ips, attack_duration):
    if time_window <= 0 or threshold_factor <= 0 or min_source_ips <= 0 or attack_duration <= 0:
        return []
    
    # Data structures per destination IP:
    # stats = {
    #   dest_ip: {
    #       'first_seen': int,
    #       'total_count': int,
    #       'window': deque of (start_time, source_ip),
    #       'attack_start': int or None
    #   }
    # }
    stats = {}
    confirmed_attacks = set()
    
    for record in flow_records:
        t = record['start_time']
        src = record['source_ip']
        dest = record['destination_ip']
        
        if dest in confirmed_attacks:
            # Already confirmed attack for this destination; update historical stats
            # but we don't need to check further since it's already detected.
            # Still update its stats for completeness.
            if dest not in stats:
                stats[dest] = {'first_seen': t, 'total_count': 0, 'window': deque(), 'attack_start': None}
            stats[dest]['total_count'] += 1
            stats[dest]['window'].append((t, src))
            # Clean up the window
            while stats[dest]['window'] and stats[dest]['window'][0][0] < t - time_window + 1:
                stats[dest]['window'].popleft()
            continue
        
        if dest not in stats:
            stats[dest] = {'first_seen': t, 'total_count': 0, 'window': deque(), 'attack_start': None}
        
        entry = stats[dest]
        entry['total_count'] += 1
        entry['window'].append((t, src))
        
        # Remove records outside the sliding window
        while entry['window'] and entry['window'][0][0] < t - time_window + 1:
            entry['window'].popleft()
        
        current_window_count = len(entry['window'])
        unique_sources = len({src_ip for (_, src_ip) in entry['window']})
        
        # Compute historical rate: total connections divided by time span
        elapsed_time = t - entry['first_seen'] + 1  # add 1 to avoid division by zero
        historical_rate = entry['total_count'] / elapsed_time
        expected_connections = historical_rate * time_window
        
        # Check if anomaly conditions are met
        if expected_connections > 0 and current_window_count > threshold_factor * expected_connections and unique_sources >= min_source_ips:
            if entry['attack_start'] is None:
                entry['attack_start'] = t
            elif t - entry['attack_start'] + 1 >= attack_duration:
                confirmed_attacks.add(dest)
        else:
            # reset attack start if anomaly conditions are not continuously met
            entry['attack_start'] = None
    
    return list(confirmed_attacks)