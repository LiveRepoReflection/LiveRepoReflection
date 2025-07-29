const { RateLimiter } = require('../distributed_wfq');

describe('Distributed WFQ Rate Limiter', () => {
  let rateLimiter;

  beforeEach(() => {
    // Initialize with two services: serviceA (weight = 1) and serviceB (weight = 3)
    // and an overall capacity of 16 requests per time window.
    rateLimiter = new RateLimiter({ serviceA: 1, serviceB: 3 }, 16);
  });

  test('should allow requests based on weights using WFQ', () => {
    // Simulate a burst of requests distributed between serviceA and serviceB.
    let serviceACount = 0;
    let serviceBCount = 0;
    const requests = [];

    // Generate 100 requests, alternating between serviceA and serviceB.
    for (let i = 0; i < 50; i++) {
      requests.push({ service: 'serviceA' });
      requests.push({ service: 'serviceB' });
    }

    // Process each request sequentially.
    requests.forEach(req => {
      if (rateLimiter.allowRequest(req.service)) {
        if (req.service === 'serviceA') {
          serviceACount++;
        } else if (req.service === 'serviceB') {
          serviceBCount++;
        }
      }
    });

    // The combined allowed requests should not exceed the overall capacity.
    expect(serviceACount + serviceBCount).toBeLessThanOrEqual(16);
    // Given the weights (1 for serviceA and 3 for serviceB),
    // serviceB should have a noticeably higher count than serviceA.
    expect(serviceBCount).toBeGreaterThanOrEqual(serviceACount * 2);
  });

  test('should deny requests exceeding the resource capacity', () => {
    // Make requests from serviceA until the resource capacity is hit.
    let allowed = 0;
    for (let i = 0; i < 100; i++) {
      if (rateLimiter.allowRequest('serviceA')) {
        allowed++;
      }
    }
    expect(allowed).toBeLessThanOrEqual(16);
  });

  test('should handle dynamic weight updates at runtime', () => {
    // Process some requests with initial weights.
    let initialAllowedServiceB = 0;
    for (let i = 0; i < 20; i++) {
      if (rateLimiter.allowRequest('serviceB')) {
        initialAllowedServiceB++;
      }
    }

    // Simulate advancement to the next time window.
    rateLimiter.resetWindow();

    // Update service weights dynamically.
    // Switch weights: serviceA becomes 3 and serviceB becomes 1.
    rateLimiter.updateWeight('serviceA', 3);
    rateLimiter.updateWeight('serviceB', 1);

    let postUpdateAllowedServiceA = 0;
    for (let i = 0; i < 20; i++) {
      if (rateLimiter.allowRequest('serviceA')) {
        postUpdateAllowedServiceA++;
      }
    }

    // With the updated weights, serviceA should now receive more requests than before.
    // We compare to ensure a noticeable change in distribution.
    expect(postUpdateAllowedServiceA).toBeGreaterThan(initialAllowedServiceB / 3);
  });

  test('should be concurrency safe when processing requests in parallel', async () => {
    // Simulate parallel execution of allowRequest calls using Promise.all.
    rateLimiter.resetWindow();
    const totalRequests = 50;
    const promises = [];

    for (let i = 0; i < totalRequests; i++) {
      promises.push(Promise.resolve().then(() => rateLimiter.allowRequest('serviceB')));
    }

    const results = await Promise.all(promises);
    const allowedCount = results.filter(result => result === true).length;
    expect(allowedCount).toBeLessThanOrEqual(16);
  });

  test('should maintain state across simulated node failures (restart simulation)', () => {
    // Process some requests before simulating a node failure.
    let firstAllowed = 0;
    for (let i = 0; i < 10; i++) {
      if (rateLimiter.allowRequest('serviceA')) {
        firstAllowed++;
      }
    }

    // Simulate node failure recovery by capturing the current state.
    const preservedState = rateLimiter.getState();
    // Create a new RateLimiter instance with the preserved state.
    rateLimiter = new RateLimiter({ serviceA: 1, serviceB: 3 }, 16, preservedState);

    let secondAllowed = 0;
    for (let i = 0; i < 10; i++) {
      if (rateLimiter.allowRequest('serviceA')) {
        secondAllowed++;
      }
    }

    // The total allowed requests across both instances should not exceed the overall capacity.
    expect(firstAllowed + secondAllowed).toBeLessThanOrEqual(16);
  });
});