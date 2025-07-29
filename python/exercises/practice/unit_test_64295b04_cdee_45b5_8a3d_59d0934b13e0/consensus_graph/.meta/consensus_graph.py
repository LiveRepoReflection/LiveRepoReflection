def consensus_graph(node_views, max_iterations):
    # Helper function to get the canonical representation of an edge
    def canonical_edge(edge):
        a, b = edge
        return (a, b) if a <= b else (b, a)

    # Convert all node views to canonical form for internal consistency
    current_views = [set(canonical_edge(edge) for edge in view) for view in node_views]

    # If there are no node views, return an empty set
    if not current_views:
        return set()

    # If no iterations allowed, return the canonicalized view of the first node
    if max_iterations == 0:
        return current_views[0].copy()

    for _ in range(max_iterations):
        # Compute the union of all views
        union_view = set()
        for view in current_views:
            union_view |= view

        # Check for convergence: all views are identical to the union_view
        if all(view == union_view for view in current_views):
            return union_view

        # Update each node's view to be the union_view for next iteration
        current_views = [union_view.copy() for _ in current_views]

    # After max_iterations, return the view of the first node
    return current_views[0].copy()