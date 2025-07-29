def run_distributed_scheduler(agents_data):
    all_events = []
    for agent, (events, neighbors) in agents_data.items():
        for index, event in enumerate(events):
            start, duration, preference = event
            all_events.append({
                "agent": agent,
                "index": index,
                "original_start": start,
                "duration": duration,
                "preference": preference,
                "adjusted_start": start
            })
    all_events.sort(key=lambda e: e["original_start"])
    processed_events = []
    def events_conflict(s1, d1, s2, d2):
        return max(s1, s2) < min(s1 + d1, s2 + d2)
    for event in all_events:
        candidate = event["adjusted_start"]
        while True:
            conflict_found = False
            max_end = candidate
            for pe in processed_events:
                if pe["agent"] != event["agent"]:
                    if events_conflict(candidate, event["duration"], pe["adjusted_start"], pe["duration"]):
                        if pe["adjusted_start"] + pe["duration"] > max_end:
                            max_end = pe["adjusted_start"] + pe["duration"]
                        conflict_found = True
            if conflict_found:
                candidate = max_end
            else:
                break
        event["adjusted_start"] = candidate
        processed_events.append(event)
    output = {}
    for agent, (events, neighbors) in agents_data.items():
        output[agent] = ([], {})
    for event in all_events:
        agent = event["agent"]
        output[agent][0].append((event["adjusted_start"], event["duration"]))
    for agent, (events, neighbors) in agents_data.items():
        skews = {}
        for n in neighbors:
            skews[n] = 0
        output[agent] = (output[agent][0], skews)
    return output