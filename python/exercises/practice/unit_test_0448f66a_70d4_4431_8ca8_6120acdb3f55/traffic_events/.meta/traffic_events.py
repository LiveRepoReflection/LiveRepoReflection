import uuid
import math

def aggregate_events(reports, radius, time_window, min_incidents, confidence_threshold):
    # Helper: compute distance between two coordinates (lat, lon) in kilometers using flat-earth approximation.
    def distance(loc1, loc2):
        lat1, lon1 = loc1
        lat2, lon2 = loc2
        return 111 * math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)
    
    n = len(reports)
    if n == 0:
        return []
    
    # Union-Find structure for clustering
    parent = list(range(n))
    
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rootX = find(x)
        rootY = find(y)
        if rootX != rootY:
            parent[rootY] = rootX

    # Compare each pair to check if they belong to the same event cluster.
    for i in range(n):
        for j in range(i + 1, n):
            dt = abs(reports[i]['timestamp'] - reports[j]['timestamp'])
            if dt <= time_window and distance(reports[i]['location'], reports[j]['location']) <= radius:
                union(i, j)
    
    clusters = {}
    for i in range(n):
        root = find(i)
        if root not in clusters:
            clusters[root] = []
        clusters[root].append(reports[i])
    
    events = []
    for cluster in clusters.values():
        if len(cluster) < min_incidents:
            continue
        
        # Check average confidence threshold:
        total_conf = sum(inc['confidence'] for inc in cluster)
        avg_conf = total_conf / len(cluster)
        if avg_conf < confidence_threshold:
            continue
        
        # Event id: generate uuid
        event_id = str(uuid.uuid4())
        
        # Determine event type: most frequent incident type in the cluster.
        type_count = {}
        for inc in cluster:
            inc_type = inc['incident_type']
            type_count[inc_type] = type_count.get(inc_type, 0) + 1
        event_type = max(type_count.keys(), key=lambda k: type_count[k])
        
        # Calculate centroid of locations
        sum_lat = sum(inc['location'][0] for inc in cluster)
        sum_lon = sum(inc['location'][1] for inc in cluster)
        centroid = (sum_lat / len(cluster), sum_lon / len(cluster))
        
        # Determine start_time (min) and end_time (max)
        start_time = min(inc['timestamp'] for inc in cluster)
        end_time = max(inc['timestamp'] for inc in cluster)
        
        # Calculate weighted severity: sum(severity * confidence) / sum(confidence)
        weighted_severity = sum(inc['severity'] * inc['confidence'] for inc in cluster) / total_conf
        
        incident_ids = [inc['incident_id'] for inc in cluster]
        
        event = {
            'event_id': event_id,
            'event_type': event_type,
            'location': centroid,
            'start_time': start_time,
            'end_time': end_time,
            'severity': weighted_severity,
            'incident_ids': incident_ids
        }
        events.append(event)
        
    return events