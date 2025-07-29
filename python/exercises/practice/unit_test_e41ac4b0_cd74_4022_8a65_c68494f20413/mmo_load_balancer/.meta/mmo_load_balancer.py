def assign_player(servers, zone):
    # Thresholds for CPU and Memory usage.
    CPU_THRESHOLD = 80
    MEMORY_THRESHOLD = 90

    # Filter out servers that are not active or are overloaded.
    candidates = []
    for server in servers:
        if not server.get("active", False):
            continue
        if server.get("cpu", 0) >= CPU_THRESHOLD or server.get("memory", 0) >= MEMORY_THRESHOLD:
            continue
        candidates.append(server)

    if not candidates:
        raise ValueError("No server available")

    # Compute a score for each candidate.
    # Lower score is preferred.
    # Score = (players / weight) + bonus, where bonus is -10 if the zone is already assigned.
    best_score = None
    chosen = None

    for server in candidates:
        weight = server.get("weight", 1.0)
        players = server.get("players", 0)
        base_score = players / weight
        if zone in server.get("zones", []):
            bonus = -10
        else:
            bonus = 0
        score = base_score + bonus

        if best_score is None or score < best_score:
            best_score = score
            chosen = server
        # In case of tie, prefer the server with zone affinity.
        elif score == best_score:
            if zone in server.get("zones", []) and zone not in chosen.get("zones", []):
                chosen = server

    # If the chosen server already has the zone, no further action is required.
    # Otherwise, add the zone to the server's zones.
    if zone not in chosen.get("zones", []):
        # Copy the zones list to avoid mutating if not intended and then update.
        zones = chosen.get("zones", [])
        zones.append(zone)
        chosen["zones"] = zones

    # Update the players count to reflect the assignment.
    chosen["players"] = chosen.get("players", 0) + 1

    return chosen["id"]