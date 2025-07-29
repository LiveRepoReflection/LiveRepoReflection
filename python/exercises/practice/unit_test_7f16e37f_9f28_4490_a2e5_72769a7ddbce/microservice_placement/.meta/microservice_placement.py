import copy

def find_optimal_placement(machines, microservices, latency):
    # Prepare machine mapping: machine_id -> machine object
    machine_dict = {m.machine_id: m for m in machines}
    # List of machine_ids in sorted order for consistency.
    machine_ids = sorted(machine_dict.keys())

    # Create dictionary to associate microservice by its id for easier lookup.
    microservice_dict = {ms.service_id: ms for ms in microservices}
    # Order microservices list. Using the order in input.
    ordered_services = microservices

    best_solution = {}
    best_cost = float('inf')

    # Setup dictionary for remaining resources for each machine id.
    def init_machine_resources():
        resources = {}
        for m in machines:
            resources[m.machine_id] = {
                'cpu': m.cpu_capacity,
                'memory': m.memory_capacity,
                'network': m.network_capacity
            }
        return resources

    # Check latency constraints for a service and its pairing with already assigned services.
    def check_latency(curr_assignment, current_service, assigned_machine):
        # Check current service against its own dependencies.
        for dep_service, max_allowed in current_service.latency_dependencies.items():
            if dep_service in curr_assignment:
                # If placed on different machines, then latency must be <= allowed.
                if curr_assignment[dep_service] != assigned_machine:
                    if latency > max_allowed:
                        return False
        # Check reverse: If any already assigned service has a dependency on the current service.
        for s_id, m_id in curr_assignment.items():
            other = microservice_dict[s_id]
            if current_service.service_id in other.latency_dependencies:
                max_allowed = other.latency_dependencies[current_service.service_id]
                if m_id != assigned_machine:
                    if latency > max_allowed:
                        return False
        return True

    # Backtracking recursion.
    def backtrack(i, curr_assignment, machine_resources, used_machines):
        nonlocal best_solution, best_cost
        # If all services are assigned, calculate cost and update best solution if needed.
        if i >= len(ordered_services):
            current_cost = len(used_machines)
            if current_cost < best_cost:
                best_cost = current_cost
                best_solution = copy.deepcopy(curr_assignment)
            return

        # Prune if current used machine count is already not promising.
        if len(used_machines) >= best_cost:
            return

        current_service = ordered_services[i]
        # Create a list of candidate machines: first try already used machines then unused sorted by machine id.
        candidates = []
        for m_id in machine_ids:
            if m_id in used_machines:
                candidates.append(m_id)
        for m_id in machine_ids:
            if m_id not in used_machines:
                candidates.append(m_id)

        # Iterate over candidate machines.
        for m_id in candidates:
            # Check capacity constraints.
            res = machine_resources[m_id]
            if (res['cpu'] < current_service.cpu_requirement or
                res['memory'] < current_service.memory_requirement or
                res['network'] < current_service.network_requirement):
                continue

            # Check latency constraints relative to already assigned services.
            if not check_latency(curr_assignment, current_service, m_id):
                continue

            # Assign current service to machine m_id.
            curr_assignment[current_service.service_id] = m_id
            # Update resources for m_id.
            machine_resources[m_id]['cpu'] -= current_service.cpu_requirement
            machine_resources[m_id]['memory'] -= current_service.memory_requirement
            machine_resources[m_id]['network'] -= current_service.network_requirement

            added_new = False
            if m_id not in used_machines:
                used_machines.add(m_id)
                added_new = True

            # Recurse to next service.
            backtrack(i + 1, curr_assignment, machine_resources, used_machines)

            # Backtrack: undo assignment.
            if added_new:
                used_machines.remove(m_id)
            machine_resources[m_id]['cpu'] += current_service.cpu_requirement
            machine_resources[m_id]['memory'] += current_service.memory_requirement
            machine_resources[m_id]['network'] += current_service.network_requirement
            del curr_assignment[current_service.service_id]

    resources_init = init_machine_resources()
    backtrack(0, {}, resources_init, set())
    return best_solution