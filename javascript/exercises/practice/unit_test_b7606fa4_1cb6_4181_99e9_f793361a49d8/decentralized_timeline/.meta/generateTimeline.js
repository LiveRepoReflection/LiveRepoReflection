async function generateTimeline(userId, instanceList, maxPosts, requestTimestamp) {
  const dedupMap = new Map();

  const instanceTasks = instanceList.map(async (instanceUrl) => {
    try {
      // Wait for the rate limit clearance for the instance.
      await rateLimit(instanceUrl);

      // Get the list of accounts the user is following on this instance.
      const follows = await getFollows(userId, instanceUrl);
      if (!Array.isArray(follows) || follows.length === 0) {
        return;
      }

      // Construct the API URL.
      const url = `${instanceUrl}/api/v1/timeline?userIds=${encodeURIComponent(follows.join(','))}&maxPosts=${maxPosts}`;

      // Fetch posts from the instance.
      const response = await fetch(url);
      const posts = await response.json();
      if (!Array.isArray(posts)) {
        return;
      }

      // Process each post.
      for (const post of posts) {
        // Calculate recency score.
        const recencyScore = 1 / (1 + ((requestTimestamp - post.timestamp) / (60 * 60 * 24)));
        // Calculate engagement score.
        const engagementScore = (post.likes + (2 * post.reposts)) / 1000;
        // Get trust score from the instance.
        const instanceTrust = getInstanceTrust(post.instanceUrl);
        // Compute overall relevance.
        const relevance = (0.6 * recencyScore) + (0.3 * engagementScore) + (0.1 * instanceTrust);
        post.relevance = relevance;

        // Deduplicate posts: if the same postId exists, retain the one with higher relevance.
        if (dedupMap.has(post.postId)) {
          const existingPost = dedupMap.get(post.postId);
          if (post.relevance > existingPost.relevance) {
            dedupMap.set(post.postId, post);
          }
        } else {
          dedupMap.set(post.postId, post);
        }
      }
    } catch (error) {
      // In case of any error (e.g., network failure), skip this instance.
      return;
    }
  });

  // Execute all instance tasks concurrently.
  await Promise.all(instanceTasks);

  // Gather all deduplicated posts.
  const allPosts = Array.from(dedupMap.values());
  // Sort posts in descending order by relevance.
  allPosts.sort((a, b) => b.relevance - a.relevance);

  // Return only up to maxPosts posts.
  return allPosts.slice(0, maxPosts);
}

module.exports = { generateTimeline };