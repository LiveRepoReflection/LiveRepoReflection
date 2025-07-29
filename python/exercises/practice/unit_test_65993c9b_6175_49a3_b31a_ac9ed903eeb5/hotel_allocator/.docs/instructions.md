## Question: Optimal Accommodation Allocation

### Problem Description:

A global technology company, "InnovAI", is hosting its annual international conference. Employees from various offices around the world will be attending. The company has secured accommodation in several hotels in the conference city. Your task is to design an algorithm to allocate employees to hotels in a way that minimizes the overall cost to the company, subject to several complex constraints.

InnovAI wants to encourage cross-departmental networking, so they impose a constraint on the maximum number of employees from the same department that can stay in a single hotel. The hotels have varying capacities and different negotiated rates per night per employee. Additionally, some employees have indicated preferences for staying with specific colleagues (positive affinity) or avoiding others (negative affinity).

The overall cost function to minimize includes hotel costs, a penalty for violating colleague affinity preferences, and a penalty for not meeting cross-departmental networking targets.

**Input:**

You will receive the following inputs:

*   `employees`: A list of dictionaries, where each dictionary represents an employee with the following keys:
    *   `id`: A unique employee identifier (string).
    *   `department`: The employee's department (string).
    *   `colleague_preferences`: A dictionary where keys are colleague IDs (strings) and values are integers representing affinity scores (positive for preferred colleagues, negative for colleagues to avoid).

*   `hotels`: A list of dictionaries, where each dictionary represents a hotel with the following keys:
    *   `id`: A unique hotel identifier (string).
    *   `capacity`: The maximum number of employees the hotel can accommodate (integer).
    *   `rate_per_night`: The cost per employee per night (integer).

*   `department_limit_per_hotel`: An integer representing the maximum number of employees from the same department allowed in a single hotel.

*   `affinity_penalty`: An integer representing the penalty incurred for each unit of negative affinity score among employees in the same hotel. Conversely, reduce this penalty for each unit of positive affinity.

*   `num_nights`: The duration of the conference in nights (integer).

*   `target_hotel_utilization`: The targeted percentage of each hotel capacity that InnovAI wants to utilize (float, between 0 and 1). An underutilization penalty will apply if a hotel is less than this percentage full.

*   `underutilization_penalty_per_employee`: An integer representing the penalty for each employee less than the target hotel utilization amount.

*   `colleague_stay_together_bonus`: An integer representing the bonus for each unit of positive affinity score among employees in the same hotel.

**Output:**

Return a dictionary representing the optimal allocation of employees to hotels. The dictionary should have the following structure:

```json
{
    "hotel_allocations": {
        "hotel_id_1": ["employee_id_1", "employee_id_2", ...],
        "hotel_id_2": ["employee_id_3", "employee_id_4", ...],
        ...
    },
    "total_cost": <total cost of the allocation (integer)>
}
```

**Constraints:**

*   Every employee must be assigned to exactly one hotel.
*   The number of employees assigned to a hotel must not exceed its capacity.
*   The number of employees from the same department in a hotel must not exceed `department_limit_per_hotel`.
*   The solution must minimize the `total_cost`.

**Total Cost Calculation:**

The `total_cost` is calculated as follows:

1.  **Hotel Costs:** Sum of (`rate_per_night` \* `num_nights`) for each employee in each hotel.
2.  **Affinity Penalties/Bonus:** Sum of `affinity_penalty` \* `(negative affinity score)` for each pair of employees in the same hotel, and sum of `colleague_stay_together_bonus` \* `(positive affinity score)` for each pair of employees in the same hotel.
3.  **Underutilization Penalty:** For each hotel, calculate the target utilization (`capacity` \* `target_hotel_utilization`). If the number of employees assigned to the hotel is less than the target utilization, add `underutilization_penalty_per_employee` \* (`target_utilization` - `number of employees assigned`) to the total cost.

**Optimization Requirements:**

The problem is NP-hard. You are not expected to find the absolute optimal solution in all cases, especially for large inputs. However, your algorithm should strive to find a good solution within a reasonable time limit (e.g., a few minutes). Consider using heuristics, approximation algorithms, or metaheuristic optimization techniques (e.g., simulated annealing, genetic algorithms).

**Edge Cases and Considerations:**

*   Handle cases where there are more employees than total hotel capacity.
*   Handle cases where some hotels are significantly more expensive than others.
*   Handle cases where affinity preferences are very strong (either positive or negative).
*   Consider the trade-off between minimizing hotel costs and satisfying affinity preferences.
*   Ensure that the algorithm scales reasonably well with the number of employees and hotels.
*   Ensure all constraints are met.

This problem challenges you to apply your knowledge of data structures, algorithms, optimization techniques, and system design to solve a complex real-world problem. Good luck!
