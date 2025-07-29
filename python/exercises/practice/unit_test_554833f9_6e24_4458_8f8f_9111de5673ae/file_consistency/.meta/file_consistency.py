def are_chunks_consistent(N, files, chunk_map, node_data):
    # For each file and its chunks, check if the replicas (non-None) across all nodes are equal.
    for file in files:
        if file not in chunk_map:
            continue
        for chunk in chunk_map[file]:
            expected = None
            for i in range(N):
                # Retrieve the data from the node; if key not present, treat as None.
                data = node_data[i].get(chunk, None)
                if data is None:
                    continue
                if expected is None:
                    expected = data
                elif expected != data:
                    return False
    return True