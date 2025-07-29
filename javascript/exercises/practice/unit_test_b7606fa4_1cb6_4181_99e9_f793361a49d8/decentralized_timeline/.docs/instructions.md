## Project Name

**Decentralized Social Network Timeline Aggregator**

## Question Description

You are tasked with designing and implementing a highly scalable and efficient timeline aggregator for a decentralized social network. This network consists of many independent nodes ("instances"), each managing a subset of user accounts and their posts. Users can follow accounts across different instances.

Your aggregator needs to fetch, merge, and rank posts from various instances to display a personalized timeline for a given user. This timeline should be sorted by a custom relevance score considering several factors:

**Input:**

*   `userId`: The ID of the user for whom the timeline is being generated.
*   `instanceList`: An array of URLs representing the instances the aggregator should query.
*   `maxPosts`: The maximum number of posts to include in the aggregated timeline.
*   `requestTimestamp`: A timestamp representing when the request was made (used for relevance calculations).

**Data Fetching:**

Each instance exposes an API endpoint `/api/v1/timeline?userIds=<comma-separated-user-ids>&maxPosts=<number>` which accepts a list of user IDs (the accounts that the target user `userId` follows on that instance) and a `maxPosts` parameter.  The API returns a JSON array of post objects.

**Post Object:**

Each post object has the following structure:

```json
{
  "postId": "unique_post_id",
  "userId": "author_user_id",
  "timestamp": 1678886400, // Unix timestamp in seconds
  "content": "Post content...",
  "likes": 123,
  "reposts": 45,
  "instanceUrl": "https://instance1.example.com" // The instance where the post originated
}
```

**Relevance Scoring:**

The relevance score for each post should be calculated as follows:

`relevance = (0.6 * recencyScore) + (0.3 * engagementScore) + (0.1 * instanceTrustScore)`

*   **Recency Score:**  `recencyScore = 1 / (1 + (requestTimestamp - post.timestamp) / (60 * 60 * 24))` (Score decays over time, with a half-life of approximately 1 day).
*   **Engagement Score:** `engagementScore = (post.likes + (2 * post.reposts)) / 1000` (Higher likes and reposts increase the score).
*   **Instance Trust Score:**  A static value representing the trustworthiness of the instance. This is provided through a function `getInstanceTrust(instanceUrl)` which returns a float between 0.0 and 1.0.  Instances with known spam or bot activity should have lower trust scores.

**Requirements:**

1.  **Scalability:** The aggregator must handle a large number of instances and user requests efficiently.
2.  **Efficiency:** Minimize the latency of timeline generation. Optimize data fetching and relevance score calculation.
3.  **Resilience:** Handle instance failures gracefully. If an instance is unreachable or returns an error, the aggregator should continue processing other instances and return a partial timeline.
4.  **Deduplication:**  If the same `postId` appears from multiple instances (due to cross-posting or federation), only include it once in the final timeline.
5.  **Follow Graph:** You are provided with a function `getFollows(userId, instanceUrl)` which returns a list of userIds that `userId` follows on that specific instance.
6.  **Prioritization:** Posts from instances with higher trust scores should be prioritized, even if their initial relevance scores are slightly lower.

**Constraints:**

*   The number of instances in `instanceList` can be very large (up to 1000).
*   Each instance might have rate limits on the API.  You must avoid exceeding these limits.  Assume you have access to a function `rateLimit(instanceUrl)` which is a promise that resolves when it's safe to make a request to the specified `instanceUrl`.
*   The `getFollows` function can be slow for some instances.
*   The `getInstanceTrust` function is relatively fast.
*   Memory usage should be kept to a reasonable level. Avoid loading the entire dataset into memory at once.
*   You *must* use Javascript.

**Output:**

An array of post objects, sorted by their relevance score in descending order, with a maximum length of `maxPosts`. Each post object should include all the original fields, plus a new field `relevance` containing the calculated relevance score. The returned array must not contain duplicate posts (based on `postId`).

**Example:**

```javascript
const userId = "user123";
const instanceList = ["https://instance1.example.com", "https://instance2.example.com", "https://instance3.example.com"];
const maxPosts = 20;
const requestTimestamp = Date.now() / 1000; // Current time in seconds

const timeline = await generateTimeline(userId, instanceList, maxPosts, requestTimestamp);

console.log(timeline);
```

Your task is to implement the `generateTimeline` function that takes the `userId`, `instanceList`, `maxPosts`, and `requestTimestamp` as input and returns the aggregated and sorted timeline.
