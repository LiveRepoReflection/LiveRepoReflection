const { generateTimeline } = require('./generateTimeline');

describe('generateTimeline', () => {
  const originalGetFollows = global.getFollows;
  const originalRateLimit = global.rateLimit;
  const originalGetInstanceTrust = global.getInstanceTrust;
  const originalFetch = global.fetch;

  beforeEach(() => {
    // Reset globals before each test
    global.getFollows = jest.fn();
    global.rateLimit = jest.fn().mockImplementation((instanceUrl) => Promise.resolve());
    global.getInstanceTrust = jest.fn().mockImplementation((instanceUrl) => {
      // Default trust value: 0.5
      return 0.5;
    });
    global.fetch = jest.fn();
  });

  afterEach(() => {
    // Restore original globals after each test
    global.getFollows = originalGetFollows;
    global.rateLimit = originalRateLimit;
    global.getInstanceTrust = originalGetInstanceTrust;
    global.fetch = originalFetch;
    jest.clearAllMocks();
  });

  test('aggregates posts from multiple instances and deduplicates posts correctly', async () => {
    const requestTimestamp = Math.floor(Date.now() / 1000);
    const instanceList = ['https://instance1.com', 'https://instance2.com'];
    const userId = 'user123';
    const maxPosts = 10;

    // Mock getFollows to return a list of followed users per instance
    global.getFollows.mockImplementation((userIdParam, instanceUrl) => {
      // For testing, return a simple list for all instances.
      return Promise.resolve(['userA', 'userB']);
    });

    // Create a mapping for fetch calls based on instance URL.
    const postsByInstance = {
      'https://instance1.com': [
        {
          postId: 'p1',
          userId: 'userA',
          timestamp: requestTimestamp - 1000,
          content: 'Post from instance1',
          likes: 100,
          reposts: 20,
          instanceUrl: 'https://instance1.com',
        },
        {
          postId: 'p2',
          userId: 'userB',
          timestamp: requestTimestamp - 1500,
          content: 'Another post from instance1',
          likes: 50,
          reposts: 10,
          instanceUrl: 'https://instance1.com',
        },
      ],
      'https://instance2.com': [
        {
          postId: 'p1', // Duplicate post (should be deduplicated)
          userId: 'userA',
          timestamp: requestTimestamp - 1000,
          content: 'Duplicate post from instance2',
          likes: 100,
          reposts: 20,
          instanceUrl: 'https://instance2.com',
        },
        {
          postId: 'p3',
          userId: 'userA',
          timestamp: requestTimestamp - 500,
          content: 'Newer post from instance2',
          likes: 200,
          reposts: 40,
          instanceUrl: 'https://instance2.com',
        },
      ],
    };

    // Mock fetch to return appropriate posts for each instance
    global.fetch.mockImplementation((url) => {
      // Extract base URL (assuming url starts with instance URL)
      let instanceUrl = '';
      try {
        const parsedUrl = new URL(url);
        instanceUrl = `${parsedUrl.protocol}//${parsedUrl.host}`;
      } catch (e) {
        return Promise.reject(new Error('Invalid URL'));
      }
      const posts = postsByInstance[instanceUrl] || [];
      return Promise.resolve({
        json: () => Promise.resolve(posts),
      });
    });

    // Customize trust values for instances
    global.getInstanceTrust.mockImplementation((instanceUrl) => {
      if (instanceUrl === 'https://instance1.com') {
        return 0.7;
      } else if (instanceUrl === 'https://instance2.com') {
        return 0.9;
      }
      return 0.5;
    });

    const timeline = await generateTimeline(userId, instanceList, maxPosts, requestTimestamp);

    // Verify that getFollows was called for each instance
    expect(global.getFollows).toHaveBeenCalledTimes(instanceList.length);
    // Verify that rateLimit was called for each instance
    expect(global.rateLimit).toHaveBeenCalledTimes(instanceList.length);
    // Verify that fetch was called for each instance with proper URL format
    expect(global.fetch).toHaveBeenCalledTimes(instanceList.length);

    // Expect deduplication: post 'p1' should appear only once.
    const postIds = timeline.map((post) => post.postId);
    const uniquePostIds = new Set(postIds);
    expect(uniquePostIds.size).toBe(postIds.length);

    // Verify that timeline is sorted by descending relevance score
    for (let i = 0; i < timeline.length - 1; i++) {
      expect(timeline[i].relevance).toBeGreaterThanOrEqual(timeline[i + 1].relevance);
    }

    // Verify that only up to maxPosts items are returned
    expect(timeline.length).toBeLessThanOrEqual(maxPosts);
  });

  test('handles instance failures gracefully', async () => {
    const requestTimestamp = Math.floor(Date.now() / 1000);
    const instanceList = ['https://instance1.com', 'https://instance_failure.com'];
    const userId = 'user456';
    const maxPosts = 5;

    global.getFollows.mockImplementation((userIdParam, instanceUrl) => {
      // For failure instance, still return a follow list
      return Promise.resolve(['userX']);
    });

    // Define fetch responses: success for instance1, error for instance_failure.com.
    global.fetch.mockImplementation((url) => {
      let instanceUrl = '';
      try {
        const parsedUrl = new URL(url);
        instanceUrl = `${parsedUrl.protocol}//${parsedUrl.host}`;
      } catch (e) {
        return Promise.reject(new Error('Invalid URL'));
      }
      if (instanceUrl === 'https://instance_failure.com') {
        return Promise.reject(new Error('Failed to fetch'));
      }
      return Promise.resolve({
        json: () =>
          Promise.resolve([
            {
              postId: 'p10',
              userId: 'userX',
              timestamp: requestTimestamp - 800,
              content: 'Post from instance1',
              likes: 80,
              reposts: 16,
              instanceUrl: 'https://instance1.com',
            },
          ]),
      });
    });

    global.getInstanceTrust.mockImplementation((instanceUrl) => {
      if (instanceUrl === 'https://instance1.com') {
        return 0.65;
      } else if (instanceUrl === 'https://instance_failure.com') {
        return 0.5;
      }
      return 0.5;
    });

    const timeline = await generateTimeline(userId, instanceList, maxPosts, requestTimestamp);

    // Expect timeline to contain posts only from the successful instance.
    expect(timeline.length).toBe(1);
    expect(timeline[0].postId).toBe('p10');
  });

  test('returns empty array when instanceList is empty', async () => {
    const requestTimestamp = Math.floor(Date.now() / 1000);
    const instanceList = [];
    const userId = 'user789';
    const maxPosts = 10;

    const timeline = await generateTimeline(userId, instanceList, maxPosts, requestTimestamp);
    expect(Array.isArray(timeline)).toBe(true);
    expect(timeline.length).toBe(0);
  });

  test('prioritizes posts from instances with higher trust scores', async () => {
    const requestTimestamp = Math.floor(Date.now() / 1000);
    const instanceList = ['https://lowtrust.com', 'https://highttrust.com'];
    const userId = 'userPriority';
    const maxPosts = 10;

    global.getFollows.mockImplementation((userIdParam, instanceUrl) => {
      return Promise.resolve(['userP']);
    });

    // Create posts with similar recency and engagement so that instance trust is the tie-breaker.
    const postsByInstance = {
      'https://lowtrust.com': [
        {
          postId: 'pL1',
          userId: 'userP',
          timestamp: requestTimestamp - 600,
          content: 'Low trust post',
          likes: 100,
          reposts: 10,
          instanceUrl: 'https://lowtrust.com',
        },
      ],
      'https://highttrust.com': [
        {
          postId: 'pH1',
          userId: 'userP',
          timestamp: requestTimestamp - 600,
          content: 'High trust post',
          likes: 100,
          reposts: 10,
          instanceUrl: 'https://highttrust.com',
        },
      ],
    };

    global.fetch.mockImplementation((url) => {
      let instanceUrl = '';
      try {
        const parsedUrl = new URL(url);
        instanceUrl = `${parsedUrl.protocol}//${parsedUrl.host}`;
      } catch (e) {
        return Promise.reject(new Error('Invalid URL'));
      }
      const posts = postsByInstance[instanceUrl] || [];
      return Promise.resolve({
        json: () => Promise.resolve(posts),
      });
    });

    global.getInstanceTrust.mockImplementation((instanceUrl) => {
      if (instanceUrl === 'https://lowtrust.com') {
        return 0.4;
      } else if (instanceUrl === 'https://highttrust.com') {
        return 0.95;
      }
      return 0.5;
    });

    const timeline = await generateTimeline(userId, instanceList, maxPosts, requestTimestamp);
    
    // Ensure both posts are present
    expect(timeline.length).toBe(2);

    // The post from the high trust instance should have a higher relevance score
    const highTrustPost = timeline.find((p) => p.postId === 'pH1');
    const lowTrustPost = timeline.find((p) => p.postId === 'pL1');
    expect(highTrustPost).toBeDefined();
    expect(lowTrustPost).toBeDefined();
    expect(highTrustPost.relevance).toBeGreaterThan(lowTrustPost.relevance);
  });
});