def search_social_graph(starting_node, search_query, max_hops, similarity_threshold):
    def jaccard_similarity(str1, str2):
        tokens1 = set(str1.lower().split())
        tokens2 = set(str2.lower().split())
        if not tokens1 and not tokens2:
            return 1.0
        union = tokens1.union(tokens2)
        if not union:
            return 0.0
        return len(tokens1.intersection(tokens2)) / len(union)

    queue = [(starting_node, 0)]
    visited = set()
    results = []

    while queue:
        node, hops = queue.pop(0)
        node_id = getattr(node, 'id', id(node))
        if node_id in visited:
            continue
        visited.add(node_id)

        for user_id, profile in node.user_profiles.items():
            sim_score = jaccard_similarity(search_query, profile)
            if sim_score >= similarity_threshold:
                results.append((user_id, sim_score))

        if hops < max_hops:
            if hasattr(node, 'network') and node.network:
                for neighbor_id in node.neighbors:
                    if neighbor_id not in visited:
                        neighbor_node = node.network.get(neighbor_id, None)
                        if neighbor_node is not None:
                            queue.append((neighbor_node, hops + 1))

    results.sort(key=lambda x: x[1], reverse=True)
    return results