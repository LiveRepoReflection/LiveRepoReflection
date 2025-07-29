from collections import deque

def simulate_information_spread(N, network, source):
    # Initialize a list to record the time when each node gets infected.
    # A value of -1 indicates the node has not been infected.
    visited = [-1] * N
    visited[source] = 0

    # Use BFS to simulate the spread of information in the network.
    q = deque([source])

    while q:
        current = q.popleft()
        for neighbor in network[current]:
            # If the neighbor hasn't been infected yet, infect it.
            if visited[neighbor] == -1:
                visited[neighbor] = visited[current] + 1
                q.append(neighbor)

    # If there is any node that was never infected, return -1.
    if -1 in visited:
        return -1

    # Otherwise, the answer is the time it takes for the farthest node to be infected.
    return max(visited)

if __name__ == '__main__':
    # For direct tests (optional)
    N = 7
    network = [
        [1, 2],
        [0, 3, 4],
        [0, 4],
        [1, 5],
        [1, 2, 5, 6],
        [3, 4],
        [4]
    ]
    source = 0
    print(simulate_information_spread(N, network, source))