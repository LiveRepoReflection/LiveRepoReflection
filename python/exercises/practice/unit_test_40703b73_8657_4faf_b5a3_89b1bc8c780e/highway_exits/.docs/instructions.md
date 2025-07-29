## Question: Optimal Highway Exit Placement

### Question Description

Imagine you are a city planner tasked with optimizing the placement of exits along a newly constructed highway. The highway spans a significant distance, and your goal is to minimize the average travel time for residents to reach the highway from their homes.

You are given the following information:

*   **Highway Length (L):** The length of the highway, represented as a straight line from 0 to L.
*   **Number of Exits (N):** The number of exits you can place along the highway.
*   **Residential Zones:** A list of M residential zones. Each zone is defined by:
    *   **Position (x\_i, y\_i):** Coordinates representing the location of the zone.  `x_i` represents the perpendicular distance from the start of the highway (position 0). `y_i` is the distance away from the highway.
    *   **Population (p\_i):** The population of the zone.
*   **Travel Speed:**
    *   **Off-Highway (v1):** The average travel speed on local roads (from a residential zone to the highway).
    *   **On-Highway (v2):** The average travel speed on the highway. Assume v2 > v1.

**Objective:**

Determine the optimal positions of the N exits along the highway (between 0 and L, inclusive) that minimize the total weighted travel time for all residents to reach the highway. The weighted travel time for a zone is the product of its population and the time it takes for residents to reach the highway using the closest exit.

**Travel Time Calculation:**

The travel time from a residential zone (x\_i, y\_i) to an exit located at position 'e' on the highway is calculated as follows:

1.  **Off-Highway Travel:** Distance from (x\_i, y\_i) to the closest point on the highway (x\_i, 0) is `y_i`. Time taken is `y_i / v1`.
2.  **Highway Travel:** Distance from (x\_i, 0) to the exit 'e' is `abs(x_i - e)`. Time taken is `abs(x_i - e) / v2`.
3.  **Total Travel Time:** `(y_i / v1) + (abs(x_i - e) / v2)`

If multiple exits exist, residents will always use the exit that provides them with the smallest total travel time.

**Constraints:**

*   1 <= N <= 100
*   1 <= M <= 1000
*   1 <= L <= 1000
*   0 <= x\_i <= L
*   1 <= y\_i <= 100
*   1 <= p\_i <= 1000
*   1 <= v1 < v2 <= 100

**Optimization Requirements:**

*   Your solution must be efficient enough to handle large values of M. A naive brute-force approach will likely time out.
*   The exit positions must be precise to at least 6 decimal places.
*   Consider edge cases where residential zones are clustered near certain points on the highway.
*   Exits do not have to be equally spaced.
*   Multiple exits can be at the same location.

**Input:**

The input consists of the following:

*   `L`: The length of the highway (integer).
*   `N`: The number of exits (integer).
*   `M`: The number of residential zones (integer).
*   `residential_zones`: A list of tuples, where each tuple represents a residential zone: `(x_i, y_i, p_i)`
*   `v1`: The off-highway travel speed (integer).
*   `v2`: The on-highway travel speed (integer).

**Output:**

A list of N floating-point numbers, representing the optimal positions of the exits along the highway, sorted in ascending order. The values should be rounded to 6 decimal places.

**Example:**

```
L = 10
N = 2
M = 3
residential_zones = [(2, 5, 10), (5, 2, 15), (8, 3, 20)]
v1 = 1
v2 = 2

# Possible optimal output (Order must be ascending):
# [2.0, 8.0]
```
