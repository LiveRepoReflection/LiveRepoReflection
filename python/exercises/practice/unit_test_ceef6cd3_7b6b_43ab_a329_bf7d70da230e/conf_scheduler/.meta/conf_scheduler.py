from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple

def detect_cycle(graph: Dict[int, List[int]], start: int, visited: Set[int], path: Set[int]) -> bool:
    """Helper function to detect cycles in the dependency graph using DFS."""
    visited.add(start)
    path.add(start)
    
    for neighbor in graph[start]:
        if neighbor not in visited:
            if detect_cycle(graph, neighbor, visited, path):
                return True
        elif neighbor in path:
            return True
    
    path.remove(start)
    return False

def has_cycle(dependencies: List[Tuple[int, int]], speakers: Dict[int, dict]) -> bool:
    """Check if there are any cycles in the speaker dependencies."""
    graph = defaultdict(list)
    for dep_a, dep_b in dependencies:
        graph[dep_a].append(dep_b)
    
    visited = set()
    path = set()
    
    for speaker in speakers:
        if speaker not in visited:
            if detect_cycle(graph, speaker, visited, path):
                return True
    return False

def topological_sort(dependencies: List[Tuple[int, int]], speakers: Dict[int, dict]) -> List[int]:
    """Return speakers in topologically sorted order based on dependencies."""
    # Build adjacency list and in-degree count
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    
    for dep_a, dep_b in dependencies:
        graph[dep_b].append(dep_a)
        in_degree[dep_a] += 1
    
    # Initialize queue with nodes having no dependencies
    queue = deque([speaker for speaker in speakers if in_degree[speaker] == 0])
    result = []
    
    while queue:
        current = queue.popleft()
        result.append(current)
        
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return result

def can_schedule_talk(
    speaker: int,
    start_time: int,
    speakers: Dict[int, dict],
    venue_schedule: Dict[int, List[Tuple[int, int]]],
    scheduled_talks: Dict[int, int]
) -> bool:
    """Check if a talk can be scheduled at the given start time."""
    talk_duration = speakers[speaker]['talk_duration']
    venue_id = speakers[speaker]['venue_requirement']
    end_time = start_time + talk_duration
    
    # Check if within speaker's availability
    is_available = False
    for avail_start, avail_end in speakers[speaker]['availability']:
        if start_time >= avail_start and end_time <= avail_end:
            is_available = True
            break
    if not is_available:
        return False
    
    # Check venue availability
    for scheduled_start, scheduled_end in venue_schedule[venue_id]:
        if not (end_time <= scheduled_start or start_time >= scheduled_end):
            return False
    
    return True

def schedule_conference(
    speakers: Dict[int, dict],
    venue_capacities: Dict[int, int],
    speaker_dependencies: List[Tuple[int, int]],
    speaker_capacities: Dict[int, int],
    conference_start_time: int,
    conference_end_time: int
) -> List[Tuple[int, int]]:
    """
    Schedule conference talks optimally while respecting all constraints.
    Returns list of (speaker_id, start_time) tuples.
    """
    # Input validation
    if not speakers:
        raise ValueError("No speakers provided")
    
    # Check for negative times and capacities
    for speaker, info in speakers.items():
        if any(t < 0 for slot in info['availability'] for t in slot):
            raise ValueError("Negative time values are not allowed")
        if info['talk_duration'] < 0:
            raise ValueError("Negative talk duration is not allowed")
        if speaker_capacities[speaker] < 0:
            raise ValueError("Negative speaker capacity is not allowed")
    
    # Check for circular dependencies
    if has_cycle(speaker_dependencies, speakers):
        raise ValueError("Circular dependencies detected")
    
    # Check venue capacities
    for speaker, info in speakers.items():
        venue_id = info['venue_requirement']
        if speaker_capacities[speaker] > venue_capacities[venue_id]:
            continue  # Skip speakers that require more capacity than available
    
    # Get speakers in topologically sorted order
    speaker_order = topological_sort(speaker_dependencies, speakers)
    
    # Initialize scheduling structures
    venue_schedule = defaultdict(list)  # venue_id -> list of (start, end) times
    scheduled_talks = {}  # speaker_id -> start_time
    
    # Try to schedule each speaker
    for speaker in speaker_order:
        talk_duration = speakers[speaker]['talk_duration']
        venue_id = speakers[speaker]['venue_requirement']
        
        # Skip if venue capacity is insufficient
        if speaker_capacities[speaker] > venue_capacities[venue_id]:
            continue
        
        # Find earliest valid time slot
        current_time = conference_start_time
        while current_time + talk_duration <= conference_end_time:
            if can_schedule_talk(speaker, current_time, speakers, venue_schedule, scheduled_talks):
                # Schedule the talk
                scheduled_talks[speaker] = current_time
                venue_schedule[venue_id].append((current_time, current_time + talk_duration))
                venue_schedule[venue_id].sort()  # Keep schedule sorted
                break
            current_time += 1
    
    # Convert result to required format and sort by start time
    result = [(speaker, time) for speaker, time in scheduled_talks.items()]
    result.sort(key=lambda x: x[1])  # Sort by start time
    
    return result