import sys
import math

class Server:
    def __init__(self, server_id, capacity, processing_speed):
        self.server_id = server_id
        self.capacity = capacity
        self.processing_speed = processing_speed
        self.active_requests = []  # list of Request objects currently being processed
        self.current_load = 0      # sum of remaining workloads of active requests

class Request:
    def __init__(self, request_id, workload, priority, submission_order):
        self.request_id = request_id
        self.workload = workload           # total workload required
        self.priority = priority
        self.remaining_work = workload     # remaining workload to complete
        self.assigned_server = None        # server id
        self.completed = False
        self.cancelled = False
        self.failed = False
        self.completion_time = None        # time at which request completed
        self.submission_order = submission_order  # used to order requests with same priority

def main():
    servers = {}  # server_id -> Server object
    pending_requests = {}  # request_id -> Request object
    cancelled_requests = set()  # set of request_ids cancelled before simulation
    simulation_parameters = None  # tuple (duration, priority_weight)
    command_lines = []
    submission_counter = 0  # to maintain order of submission

    # Read commands from stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        if line == "END":
            break
        command_lines.append(line)

    # Process commands until SIMULATE is encountered.
    simulate_command = None
    for cmd in command_lines:
        parts = cmd.split()
        if not parts:
            continue
        command = parts[0]
        if command == "ADD_SERVER":
            # Format: ADD_SERVER server_id capacity processing_speed
            if len(parts) != 4:
                continue
            server_id = parts[1]
            capacity = int(parts[2])
            processing_speed = int(parts[3])
            # Add server to pool
            servers[server_id] = Server(server_id, capacity, processing_speed)
        elif command == "REMOVE_SERVER":
            # Format: REMOVE_SERVER server_id
            if len(parts) != 2:
                continue
            server_id = parts[1]
            if server_id in servers:
                # For any pending request assigned to this server, mark as failed.
                server = servers[server_id]
                for req in server.active_requests:
                    req.failed = True
                # Remove server from pool.
                del servers[server_id]
        elif command == "SUBMIT_REQUEST":
            # Format: SUBMIT_REQUEST request_id workload priority
            if len(parts) != 4:
                continue
            request_id = parts[1]
            workload = int(parts[2])
            priority = int(parts[3])
            submission_counter += 1
            req = Request(request_id, workload, priority, submission_counter)
            pending_requests[request_id] = req
        elif command == "CANCEL_REQUEST":
            # Format: CANCEL_REQUEST request_id
            if len(parts) != 2:
                continue
            request_id = parts[1]
            # Mark as cancelled if present in pending requests.
            if request_id in pending_requests:
                pending_requests[request_id].cancelled = True
                cancelled_requests.add(request_id)
        elif command == "SIMULATE":
            # Format: SIMULATE duration priority_weight
            if len(parts) != 3:
                continue
            duration = int(parts[1])
            priority_weight = float(parts[2])
            simulation_parameters = (duration, priority_weight)
            # Once SIMULATE is encountered, we assume no further processing commands affect simulation.
            # Break out of loop (if any commands exist after SIMULATE they are ignored).
            break

    if simulation_parameters is None:
        return

    duration, priority_weight = simulation_parameters

    # Metrics counters
    completed_count = 0
    cancelled_count = len(cancelled_requests)
    failed_count = 0
    total_response_time = 0
    response_time_count = 0
    max_load_percentage = 0

    # Assign pending requests to servers based on the modified least loaded algorithm.
    # Sort pending requests in descending order of priority, and by submission order in case of ties.
    assignable_requests = sorted(
        [req for req in pending_requests.values() if not req.cancelled],
        key=lambda r: (-r.priority, r.submission_order)
    )

    for req in assignable_requests:
        candidate_server = None
        min_weighted_load = math.inf
        # For each available server, check if it can accommodate the new request.
        for srv in servers.values():
            if srv.current_load + req.workload > srv.capacity:
                continue
            # Compute weighted load: (current_load / capacity) * (1 - (priority_weight * request.priority))
            load_ratio = srv.current_load / srv.capacity if srv.capacity > 0 else 1
            weighted_load = load_ratio * (1 - priority_weight * req.priority)
            if weighted_load < min_weighted_load:
                min_weighted_load = weighted_load
                candidate_server = srv
        if candidate_server is not None:
            # Assign request to candidate_server
            req.assigned_server = candidate_server.server_id
            candidate_server.active_requests.append(req)
            candidate_server.current_load += req.workload
        else:
            # No server could accommodate the request, mark it as failed.
            req.failed = True

    # Count failed requests among unassigned ones.
    for req in pending_requests.values():
        if req.failed:
            failed_count += 1

    # Simulation: process each server's active requests over time.
    # We simulate second by second.
    for t in range(1, duration + 1):
        for srv in list(servers.values()):
            # Process requests in the order they were assigned
            remaining_throughput = srv.processing_speed
            new_active_requests = []
            # sort active requests by submission order to simulate FIFO
            srv.active_requests.sort(key=lambda r: r.submission_order)
            for req in srv.active_requests:
                # Skip if request is already completed, cancelled or failed.
                if req.completed or req.cancelled or req.failed:
                    continue
                # Process current request
                if remaining_throughput <= 0:
                    new_active_requests.append(req)
                    continue
                work_done = min(remaining_throughput, req.remaining_work)
                req.remaining_work -= work_done
                remaining_throughput -= work_done
                # Reduce server's current load by the work done
                srv.current_load -= work_done
                if req.remaining_work <= 0:
                    req.completed = True
                    req.completion_time = t
                    completed_count += 1
                    total_response_time += t  # response time measured from time 0
                    response_time_count += 1
                else:
                    new_active_requests.append(req)
            srv.active_requests = new_active_requests
            # Update maximum load percentage for this server at this second.
            load_percentage = (srv.current_load / srv.capacity) * 100 if srv.capacity > 0 else 0
            if load_percentage > max_load_percentage:
                max_load_percentage = load_percentage

    # For any requests still in active_requests after simulation time, treat them as incomplete.
    # They are not counted as completed but we do not mark them cancelled or failed.
    # We leave them out of average response time.

    average_response_time = total_response_time / response_time_count if response_time_count > 0 else 0

    # Also count requests that were assigned but never processed because their servers were removed before simulation.
    # (They are already marked as failed during removal.)
    for req in pending_requests.values():
        if req.assigned_server is None and (not req.cancelled) and (not req.failed):
            failed_count += 1

    # Output the collected metrics.
    print("Average Response Time: {:.2f}".format(average_response_time))
    print("Maximum Load: {:.2f}%".format(max_load_percentage))
    print("Completed Requests: {}".format(completed_count))
    print("Cancelled Requests: {}".format(cancelled_count))
    print("Failed Requests: {}".format(failed_count))


if __name__ == '__main__':
    main()