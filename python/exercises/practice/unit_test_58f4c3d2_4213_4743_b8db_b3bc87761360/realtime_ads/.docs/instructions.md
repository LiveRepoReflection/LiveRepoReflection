Okay, here's a challenging Python coding problem designed to be on par with LeetCode Hard difficulty, incorporating elements of advanced data structures, optimization, and a real-world scenario:

## Question: Real-Time Recommendation Engine with Contextual Bandits

### Question Description

You are tasked with designing and implementing a simplified real-time recommendation engine for an online advertising platform. The platform displays a series of ads to users, and your goal is to maximize the click-through rate (CTR) by learning which ads are most effective for different user contexts.

**Core Requirements:**

1.  **Contextual Information:** Each user visit is characterized by a context vector `C`. This vector represents user features (e.g., location, demographics, browsing history). Assume `C` is a list of `d` floating-point numbers.
2.  **Ad Inventory:** The platform has `k` different ads to display. Each ad `i` has a feature vector `A[i]` of the same dimension `d` as the context vector `C`.
3.  **Exploration-Exploitation Tradeoff:** You must implement a contextual bandit algorithm to balance exploration (trying out different ads) and exploitation (showing the ad predicted to have the highest CTR).
4.  **Real-Time Updates:** The system must be able to process user visits and update its model in real-time.
5.  **Optimization:** The system needs to be optimized for both prediction speed (serving ads) and model update speed.
6.  **Memory Constraint**: The available memory is limited and should be used efficiently. This constraint will force candidates to think carefully about what needs to be stored and how.

**Specific Implementation Details:**

*   **Contextual Bandit Algorithm:** Implement the LinUCB (Linear Upper Confidence Bound) algorithm for contextual bandits. The algorithm maintains a separate linear model for each ad.
*   **Model Representation:** For each ad `i`, maintain two matrices:
    *   `A[i]`: A `d x d` matrix, initially the identity matrix (`I`).
    *   `b[i]`: A `d x 1` vector, initially a zero vector.

*   **Prediction:** For a given context vector `C`, the algorithm predicts the expected reward (CTR) for each ad `i` as follows:
    *   `theta[i] = A[i]^-1 * b[i]` (where `A[i]^-1` is the inverse of `A[i]`)
    *   `p[i] = C^T * theta[i] + alpha * sqrt(C^T * A[i]^-1 * C)` (where `C^T` is the transpose of `C`, and `alpha` is an exploration parameter)
    *   Select the ad `i` with the highest `p[i]`.

*   **Update:** After displaying an ad and observing a reward (0 for no click, 1 for click), update the model for the chosen ad `i`:
    *   `A[i] = A[i] + C * C^T`
    *   `b[i] = b[i] + reward * C`

**Input:**

*   `d`: The dimension of the context and ad feature vectors (an integer).
*   `k`: The number of ads (an integer).
*   `alpha`: The exploration parameter (a float).
*   A stream of user visits. Each visit is represented as a tuple: `(context_vector, chosen_ad, reward)`.
    *   `context_vector`: A list of `d` floats.
    *   `chosen_ad`: The index of the ad that was displayed (an integer between 0 and `k-1`).
    *   `reward`: 0 or 1 (an integer).

**Output:**

The system should provide two functions:

1.  `choose_ad(context_vector)`: Given a context vector, return the index of the ad to display.
2.  `update(context_vector, chosen_ad, reward)`: Update the model after observing the reward for the chosen ad.

**Constraints:**

*   `1 <= d <= 50`
*   `1 <= k <= 20`
*   `0.0 <= alpha <= 1.0`
*   The number of user visits in the stream can be very large (e.g., millions).
*   Your solution must be efficient in terms of both time and memory.  Avoid storing the entire history of context vectors and rewards. Pre-computation is allowed in the initialization phase.

**Scoring:**

Your solution will be evaluated based on the cumulative reward (total number of clicks) achieved over a large number of user visits. Solutions will also be judged on their efficiency (execution time and memory usage).

**Hints:**

*   Consider using NumPy for efficient matrix operations.
*   The `numpy.linalg.inv` function can be used to compute the inverse of a matrix.  However, computing the inverse directly can be slow. Think about alternative methods if performance becomes an issue. Sherman-Morrison formula could be useful.
*   Optimize your code to minimize the number of matrix inversions performed.
*   Be mindful of memory usage. Avoid creating large intermediate data structures.
*   Handle potential numerical instability issues when computing matrix inverses (e.g., using regularization or checking for near-singular matrices).

This problem requires a solid understanding of contextual bandit algorithms, linear algebra, and optimization techniques. Good luck!
