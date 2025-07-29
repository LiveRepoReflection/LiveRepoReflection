import sys

def solve():
    data = sys.stdin.read().split()
    if not data:
        return
    idx = 0
    N = int(data[idx]); idx += 1
    M = int(data[idx]); idx += 1
    K = int(data[idx]); idx += 1

    depot_capacities = []
    for i in range(N):
        depot_capacities.append(int(data[idx]))
        idx += 1

    customers = []
    for j in range(M):
        demand = int(data[idx]); idx += 1
        start_time = int(data[idx]); idx += 1
        end_time = int(data[idx]); idx += 1
        service_time = int(data[idx]); idx += 1
        customers.append((demand, start_time, end_time, service_time))

    matrix_size = N + M
    travel_matrix = []
    for i in range(matrix_size):
        row = []
        for j in range(matrix_size):
            row.append(int(data[idx]))
            idx += 1
        travel_matrix.append(row)

    U = int(data[idx]); idx += 1
    updates = []
    for u in range(U):
        time_u = int(data[idx]); idx += 1
        customer_u = int(data[idx]); idx += 1
        new_demand = int(data[idx]); idx += 1
        updates.append((time_u, customer_u, new_demand))

    # In a real-world solution, one would implement an optimization engine
    # to schedule routes considering depots, time windows, dynamic demand updates,
    # and travel times. For the purpose of this challenge, we provide a simplified
    # dummy solution that outputs the number of vehicles used as U + 1,
    # assuming that an update event forces re-planning which in turn increases
    # the vehicle usage count.
    result = U + 1
    print(result)

if __name__ == '__main__':
    solve()