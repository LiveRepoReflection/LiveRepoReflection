from itertools import chain, combinations
from collections import deque, defaultdict

def min_communication_cost(N, subscriptions, publications, request_dependencies, topic_costs):
    # Build dependency graph (directed) from request_dependencies.
    dep_graph = defaultdict(list)
    for i in range(N):
        for dep in request_dependencies[i]:
            dep_graph[i].append(dep)
    
    # Compute transitive dependencies for each service.
    # For each service i, find all services j such that i depends (directly or transitively) on j.
    trans_deps = [set() for _ in range(N)]
    for i in range(N):
        visited = set()
        stack = list(request_dependencies[i])
        while stack:
            cur = stack.pop()
            if cur in visited:
                continue
            visited.add(cur)
            for nxt in request_dependencies[cur]:
                if nxt not in visited:
                    stack.append(nxt)
        trans_deps[i] = visited

    # Determine candidate topics: only consider topics that appear in at least one publication and one subscription.
    candidate_topics = set()
    topic_in_pub = defaultdict(set)
    topic_in_sub = defaultdict(set)
    
    for i in range(N):
        for t in publications[i]:
            topic_in_pub[t].add(i)
        for t in subscriptions[i]:
            topic_in_sub[t].add(i)

    for t in topic_costs:
        if t in topic_in_pub and t in topic_in_sub and topic_in_pub[t] and topic_in_sub[t]:
            candidate_topics.add(t)
    candidate_topics = list(candidate_topics)
    
    # If no dependency exists, cost is 0.
    dependency_exists = any(trans_deps[i] for i in range(N))
    if not dependency_exists:
        return 0

    # Utility function: build the communication graph for a given set of topics.
    def build_comm_graph(topics_set):
        graph = defaultdict(set)
        for t in topics_set:
            for pub_service in topic_in_pub[t]:
                for sub_service in topic_in_sub[t]:
                    graph[pub_service].add(sub_service)
        return graph

    # Utility function: check if for a given communication graph, all dependency requirements are satisfied.
    def check_comm_graph(graph):
        # For each service i, for each dependency service d in transitive requirement,
        # check if there's a path from d to i in the graph.
        for i in range(N):
            for d in trans_deps[i]:
                if not path_exists(graph, d, i, N):
                    return False
        return True

    # Utility function: check reachability from start to target in the graph.
    def path_exists(graph, start, target, N):
        visited = [False] * N
        dq = deque([start])
        visited[start] = True
        while dq:
            cur = dq.popleft()
            if cur == target:
                return True
            for nxt in graph[cur]:
                if not visited[nxt]:
                    visited[nxt] = True
                    dq.append(nxt)
        return False

    # Generate all possible subsets of candidate topics using power set.
    def powerset(iterable):
        s = list(iterable)
        return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
    
    best = float('inf')
    for subset in powerset(candidate_topics):
        topics_set = set(subset)
        # Build communication graph for this subset
        graph = build_comm_graph(topics_set)
        if check_comm_graph(graph):
            cost = sum(topic_costs[t] for t in topics_set)
            if cost < best:
                best = cost

    return best if best != float('inf') else -1

if __name__ == "__main__":
    # For simple ad-hoc testing if necessary:
    import sys
    # This module is intended to be used with the unit tests.
    sys.exit(0)