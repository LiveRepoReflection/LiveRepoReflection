from collections import defaultdict
import heapq

def schedule_conference(talks, attendees, affinity_groups, k):
    # Preprocess data
    talk_info = {talk['talk_id']: {
        'capacity': talk['capacity'],
        'preferred': set(talk['preferred_attendees']),
        'assigned': set()
    } for talk in talks}
    
    attendee_info = {attendee['attendee_id']: {
        'preferred': set(attendee['preferred_talks']),
        'affinity': attendee['affinity_group_id']
    } for attendee in attendees}
    
    # Group attendees by affinity groups
    affinity_members = defaultdict(list)
    for attendee in attendees:
        affinity_members[attendee['affinity_group_id']].append(attendee['attendee_id'])
    
    # Calculate potential scores for each talk-affinity group pair
    talk_scores = defaultdict(dict)
    for talk_id, talk in talk_info.items():
        for group_id, members in affinity_members.items():
            preferred_members = [m for m in members if m in talk['preferred']]
            if not preferred_members:
                continue
            
            group_size = len(members)
            subgroup_size = min(len(preferred_members), talk['capacity'])
            
            # Score calculation
            base_score = len(preferred_members)  # Individual preferences
            affinity_score = k * subgroup_size if subgroup_size == group_size else subgroup_size
            total_score = base_score + affinity_score
            
            talk_scores[talk_id][group_id] = {
                'score': total_score,
                'members': preferred_members,
                'size': subgroup_size
            }
    
    # Priority queue for selecting best assignments
    assignments = defaultdict(set)
    remaining_capacity = {talk_id: talk['capacity'] for talk_id, talk in talk_info.items()}
    
    # Greedy assignment using priority queue
    heap = []
    for talk_id, group_scores in talk_scores.items():
        for group_id, score_info in group_scores.items():
            heapq.heappush(heap, (-score_info['score'], talk_id, group_id, score_info))
    
    assigned_attendees = set()
    
    while heap and remaining_capacity:
        _, talk_id, group_id, score_info = heapq.heappop(heap)
        
        if talk_id not in remaining_capacity:
            continue
        
        # Check if we can assign this group
        available = min(remaining_capacity[talk_id], score_info['size'])
        if available <= 0:
            continue
        
        # Assign members
        members_to_assign = [m for m in score_info['members'] if m not in assigned_attendees][:available]
        if not members_to_assign:
            continue
        
        assignments[talk_id].update(members_to_assign)
        assigned_attendees.update(members_to_assign)
        remaining_capacity[talk_id] -= len(members_to_assign)
        
        if remaining_capacity[talk_id] == 0:
            del remaining_capacity[talk_id]
    
    # Assign remaining attendees to any available talks
    unassigned = set(attendee_info.keys()) - assigned_attendees
    for attendee_id in unassigned:
        preferred_talks = attendee_info[attendee_id]['preferred']
        for talk_id in preferred_talks:
            if talk_id in remaining_capacity and remaining_capacity[talk_id] > 0:
                assignments[talk_id].add(attendee_id)
                remaining_capacity[talk_id] -= 1
                break
    
    return dict(assignments)