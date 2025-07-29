## Problem: Scalable Real-Time Bidding (RTB) System

**Description:**

You are tasked with designing and implementing a core component of a real-time bidding (RTB) system for online advertising. This component is responsible for efficiently processing incoming bid requests, matching them against a vast database of targeting criteria, and determining the optimal bid price within a strict latency budget.

**Input:**

Your system will receive a continuous stream of bid requests. Each bid request is represented as a dictionary with the following keys:

*   `request_id`: A unique string identifier for the request.
*   `user_id`: A string representing the user being targeted.
*   `device`: A string representing the device type (e.g., "desktop", "mobile", "tablet").
*   `location`: A dictionary containing geographical information:
    *   `country`: A string representing the country code (e.g., "US", "CA", "GB").
    *   `region`: A string representing the region (e.g., "California", "Ontario", "London").
    *   `city`: A string representing the city (e.g., "Los Angeles", "Toronto", "London").
*   `ad_categories`: A list of strings representing the categories of the advertisement being requested (e.g., ["sports", "news"]).

**Targeting Criteria:**

You are provided with a large database of targeting criteria. Each criterion is represented as a dictionary with the following keys:

*   `criterion_id`: A unique string identifier for the criterion.
*   `target_user_ids`: A set of user IDs that match this criterion.
*   `target_devices`: A set of device types that match this criterion.
*   `target_locations`: A set of location criteria. Each location criterion is a dictionary with the following keys:
    *   `country`: A string representing the country code. Use "*" to match any country.
    *   `region`: A string representing the region. Use "*" to match any region.
    *   `city`: A string representing the city. Use "*" to match any city.
*   `target_ad_categories`: A set of ad categories that match this criterion.
*   `bid_price`: A float representing the bid price for this criterion.

The targeting criteria database is very large (millions of entries) and stored in memory.

**Output:**

For each incoming bid request, your system must return a dictionary with the following keys:

*   `request_id`: The `request_id` from the input.
*   `bid_price`: The optimal bid price based on the matching targeting criteria. If no criteria match, the `bid_price` should be 0.0.

**Matching Logic:**

A targeting criterion matches a bid request if *all* of the following conditions are met:

1.  The `user_id` from the bid request is in the `target_user_ids` set of the criterion *or* the `target_user_ids` set is empty.
2.  The `device` from the bid request is in the `target_devices` set of the criterion *or* the `target_devices` set is empty.
3.  There exists a location criterion in the `target_locations` list of the targeting criteria that matches the `location` from the bid request. A location criterion matches if:
    *   The location criterion's `country` matches the bid request's `country` *or* the location criterion's `country` is "\*".
    *   The location criterion's `region` matches the bid request's `region` *or* the location criterion's `region` is "\*".
    *   The location criterion's `city` matches the bid request's `city` *or* the location criterion's `city` is "\*".
4.  At least one of the `ad_categories` from the bid request is present in the `target_ad_categories` set of the criterion *or* the `target_ad_categories` set is empty.

**Optimization Requirements:**

*   **Latency:**  Your system must process each bid request within a strict latency budget (e.g., 10 milliseconds). Exceeding this latency will result in missed bidding opportunities.
*   **Scalability:**  Your system must be able to handle a high volume of concurrent bid requests (e.g., thousands per second).
*   **Memory Usage:** While the entire targeting criteria database is loaded in memory, minimizing memory footprint is important for cost-effectiveness.

**Constraints:**

*   The solution must be implemented in Python.
*   You are allowed to use standard Python libraries and data structures. However, the use of specialized external libraries (e.g., for specialized indexing) is strongly discouraged unless it provides a significant performance benefit.
*   The targeting criteria database is read-only and does not change during the execution of your system.
*   The number of ad categories is relatively small (e.g., less than 100).
*   The sets `target_user_ids`, `target_devices`, and `target_ad_categories` can be empty, which means that the criterion matches any value for that field.

**Evaluation:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:**  The accuracy of the bid price calculation.
*   **Latency:**  The average processing time per bid request.
*   **Throughput:**  The number of bid requests processed per second.
*   **Code Quality:**  The clarity, maintainability, and efficiency of your code.

**Challenge:**

Develop a highly optimized system that efficiently processes bid requests against a large database of targeting criteria, meets the strict latency budget, and scales to handle a high volume of concurrent requests.  Consider the trade-offs between different data structures and algorithms to achieve the best possible performance. Think about how to pre-process the targeting criteria database to speed up the matching process. Good luck!
