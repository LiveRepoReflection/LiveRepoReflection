import itertools
import math
from collections import defaultdict

def allocate_hotels(
    employees,
    hotels,
    department_limit_per_hotel,
    affinity_penalty,
    num_nights,
    target_hotel_utilization,
    underutilization_penalty_per_employee,
    colleague_stay_together_bonus
):
    # Validate input capacity
    total_capacity = sum(h['capacity'] for h in hotels)
    if len(employees) > total_capacity:
        raise ValueError("Insufficient hotel capacity for all employees")

    # Preprocess employee data for faster access
    employee_data = {e['id']: e for e in employees}
    department_counts = defaultdict(int)
    for e in employees:
        department_counts[e['department']] += 1

    # Initialize best solution tracking
    best_solution = None
    best_cost = float('inf')

    # Generate all possible hotel assignments (heuristic approach for larger inputs)
    def generate_assignments(current_assignment, remaining_employees, hotel_index):
        nonlocal best_solution, best_cost

        if not remaining_employees:
            # Calculate total cost for this assignment
            total_cost = 0
            hotel_allocations = defaultdict(list)
            department_counts_per_hotel = defaultdict(lambda: defaultdict(int))

            for emp_id, hotel_id in current_assignment.items():
                hotel_allocations[hotel_id].append(emp_id)
                emp = employee_data[emp_id]
                department_counts_per_hotel[hotel_id][emp['department']] += 1

            # Check department constraints
            for hotel_id, dept_counts in department_counts_per_hotel.items():
                for dept, count in dept_counts.items():
                    if count > department_limit_per_hotel:
                        return  # Skip invalid assignments

            # Calculate hotel costs
            for hotel in hotels:
                emp_count = len(hotel_allocations.get(hotel['id'], []))
                total_cost += emp_count * hotel['rate_per_night'] * num_nights

                # Calculate underutilization penalty
                target_utilization = math.ceil(hotel['capacity'] * target_hotel_utilization)
                if emp_count < target_utilization:
                    total_cost += (target_utilization - emp_count) * underutilization_penalty_per_employee

            # Calculate affinity costs/benefits
            for hotel_id, emp_ids in hotel_allocations.items():
                for emp1, emp2 in itertools.combinations(emp_ids, 2):
                    emp1_prefs = employee_data[emp1]['colleague_preferences']
                    emp2_prefs = employee_data[emp2]['colleague_preferences']

                    # Check both directions for preferences
                    if emp2 in emp1_prefs:
                        score = emp1_prefs[emp2]
                        if score > 0:
                            total_cost -= score * colleague_stay_together_bonus
                        else:
                            total_cost += abs(score) * affinity_penalty

                    if emp1 in emp2_prefs:
                        score = emp2_prefs[emp1]
                        if score > 0:
                            total_cost -= score * colleague_stay_together_bonus
                        else:
                            total_cost += abs(score) * affinity_penalty

            # Update best solution if better
            if total_cost < best_cost:
                best_cost = total_cost
                best_solution = {
                    'hotel_allocations': {k: v for k, v in hotel_allocations.items()},
                    'total_cost': total_cost
                }
            return

        # Try assigning next employee to each hotel with capacity
        emp_id = remaining_employees[0]
        for hotel in hotels:
            current_count = sum(1 for e, h in current_assignment.items() if h == hotel['id'])
            if current_count < hotel['capacity']:
                new_assignment = current_assignment.copy()
                new_assignment[emp_id] = hotel['id']
                generate_assignments(new_assignment, remaining_employees[1:], hotel_index)

    # Start with empty assignment and all employees remaining
    generate_assignments({}, [e['id'] for e in employees], 0)

    if best_solution is None:
        raise ValueError("No valid allocation found that satisfies all constraints")

    return best_solution