## Question: Optimal Conference Scheduling with Affinity Grouping

**Problem Description:**

You are organizing a large, multi-day conference with a diverse set of talks. Each attendee has pre-registered, indicating their preferred talks and their "affinity group" - a group of colleagues or friends they wish to sit near during the conference.

Each talk has a limited capacity. The goal is to schedule attendees to talks in a way that maximizes overall attendee satisfaction while respecting capacity limits and affinity group seating preferences.

**Specifics:**

*   **Input:**
    *   A list of `Talks`. Each `Talk` has:
        *   A unique `talk_id` (integer).
        *   A `capacity` (integer).
        *   A `set` of attendees that "preferred" to attend this talk represented by unique `attendee_id` (integer).
    *   A list of `Attendees`. Each `Attendee` has:
        *   A unique `attendee_id` (integer).
        *   A list of `talk_id` that the attendee preferred.
        *   An `affinity_group_id` (integer). Attendees with the same `affinity_group_id` want to sit together.
    *   A list of `affinity_group_id`. For each `affinity_group_id` we know the group `size`.

*   **Output:**
    *   A dictionary mapping each `talk_id` to a `set` of `attendee_id` assigned to that talk.

*   **Constraints:**
    *   **Capacity:** The number of attendees assigned to each talk cannot exceed its `capacity`.
    *   **Preference:** Each attendee can be assigned to at most one talk.
    *   **Affinity Grouping:** Maximize the number of affinity groups that are fully seated together in the same talk, or are split into as few subgroups as possible. A subgroup of size `n` seated together contributes `n` to the overall score. A group of size `n` split into `n` subgroups of size 1 is highly undesirable.
    *   **Optimization:** The solution should maximize the total "satisfaction score". The satisfaction score is calculated as follows:
        *   +1 point for each attendee assigned to a talk they preferred.
        *   + `k` points for each member of a fully seated affinity group (all members of the group are in the same talk), where `k` is a parameter provided as input.
        *   + `n` points for each subgroup with `n` members seated together in a talk.

*   **Scoring:**
    *   The solution will be scored based on the total satisfaction score achieved. Higher scores are better.
    *   Solutions that violate the hard constraints (capacity, preference) will receive a score of 0.

*   **Edge Cases and Considerations:**
    *   Some attendees may have very few talk preferences, making it difficult to satisfy their preferences.
    *   Affinity groups may be very large, making it difficult to seat them together.
    *   The total number of attendees may exceed the total capacity of all talks, requiring strategic prioritization.
    *   Multiple optimal solutions may exist.
    *   The value of `k` will affect the weighting between individual preferences and affinity group satisfaction.

*   **Algorithmic Efficiency:**
    *   The number of talks, attendees, and affinity groups can be large (e.g., thousands). Solutions must be reasonably efficient.
    *   Brute-force approaches will not be feasible.
    *   Consider using appropriate data structures and algorithms to optimize performance.

This problem requires a combination of graph algorithms (to represent the relationships between attendees and talks), optimization techniques (to maximize the satisfaction score), and careful handling of edge cases and constraints. Good luck!
