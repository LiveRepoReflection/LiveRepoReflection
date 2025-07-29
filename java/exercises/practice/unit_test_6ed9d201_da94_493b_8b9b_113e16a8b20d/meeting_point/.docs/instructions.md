## Question: Optimal Meeting Point

### Question Description

Imagine you are developing a location-based service for a social network. Users of this network are geographically distributed, and the service aims to facilitate spontaneous meetups between users within a certain proximity of each other.

Given a set of users represented by their geographical coordinates (latitude and longitude) and a communication radius `R`, your task is to find the optimal meeting point that minimizes the total communication cost for all users within the communication radius of each other.

**Specifically:**

1.  **Input:** A list of `User` objects, where each `User` object has the following properties:
    *   `latitude`: Latitude of the user's location (double).
    *   `longitude`: Longitude of the user's location (double).
    *   `id`: A unique ID representing the user (integer).

2.  **Communication Radius (R):** A double value representing the maximum distance (in kilometers) a user can communicate to another user. Two users can communicate with each other if their geographical distance is less than or equal to `R`.

3.  **Communication Cost:** The communication cost between two users is defined as the Euclidean distance (in kilometers) between their locations. The total communication cost for a given meeting point is the sum of the communication costs from that meeting point to each user within the communication radius of each other.

4.  **Optimal Meeting Point:** The optimal meeting point is the geographical coordinate (latitude, longitude) that minimizes the total communication cost to all reachable users. You need to find the approximate optimal location.

5.  **Constraints and Edge Cases:**

    *   The number of users can be very large (up to 100,000).
    *   The communication radius `R` can vary significantly (e.g., 100 meters to 100 kilometers).
    *   Users may be clustered in certain areas or sparsely distributed.
    *   Consider edge cases such as when there are no users, or when no users are within the communication radius of each other.
    *   Latitude and longitude values are standard doubles.
    *   The function must handle cases where all users are at the exact same location.

6.  **Output:** Return an `OptimalMeetingPoint` object with the following properties:

    *   `latitude`: Latitude of the optimal meeting point (double).
    *   `longitude`: Longitude of the optimal meeting point (double).
    *   `totalCommunicationCost`: The total communication cost from the optimal meeting point to all reachable users (double).

7.  **Optimization Requirements:**

    *   The solution should be efficient in terms of both time and space complexity. A naive brute-force approach will likely time out for large datasets.
    *   Consider using appropriate data structures and algorithms to optimize the search for the optimal meeting point.
    *   The accuracy of the optimal meeting point is important, but it's acceptable to return an approximate solution within a reasonable error tolerance.
    *   The function must be able to complete execution within reasonable time limits (e.g., a few seconds) for large datasets.

8.  **Practical Considerations:**

    *   The problem is inspired by real-world scenarios such as organizing meetups, coordinating delivery services, and optimizing wireless communication networks.
    *   The solution should be robust and handle various edge cases and input variations.
    *   The problem can be approached using various techniques, including iterative optimization algorithms, spatial indexing, and approximation methods.
    *   You are free to use standard mathematical formulas and libraries for calculating geographical distances.

9. **Tie Breaking:**
    * If there are multiple optimal meeting points with the same minimum total communication cost, return any one of them.

**Important Considerations:**

*   **Distance Calculation:** Use the Haversine formula to calculate the geographical distance between two points on the Earth's surface.
*   **Efficiency:** Avoid unnecessary calculations and data structures.
*   **Testability:** Design the solution to be easily testable with various input datasets and scenarios.
*   **Scalability:** The solution should scale well with the number of users and the communication radius.

This problem requires a combination of algorithmic thinking, data structure knowledge, and optimization techniques to develop an efficient and accurate solution. Good luck!
