const http = require('http');
const https = require('https');

function sendPost(url, timeout = 5000) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const options = {
      method: 'POST',
      hostname: parsedUrl.hostname,
      port: parsedUrl.port,
      path: parsedUrl.pathname,
      timeout: timeout,
    };
    const lib = parsedUrl.protocol === 'https:' ? https : http;
    const req = lib.request(options, (res) => {
      res.on('data', () => {}); // Consume data to free up memory
      res.on('end', () => {
        resolve(res.statusCode);
      });
    });
    req.on('error', (err) => {
      reject(err);
    });
    req.on('timeout', () => {
      req.destroy(new Error('Request timed out'));
    });
    req.end();
  });
}

async function postWithRetry(url, maxRetries = 3, initialDelay = 100) {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const status = await sendPost(url, 5000);
      if (status === 200) {
        return;
      }
    } catch (err) {
      // continue to retry if error occurs
    }
    if (attempt < maxRetries) {
      const delay = initialDelay * Math.pow(2, attempt);
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }
  throw new Error(`Failed request to ${url} after ${maxRetries + 1} attempts`);
}

async function coordinateTransaction(participants) {
  // Phase 1: Prepare Phase
  const preparePromises = participants.map((participant) =>
    sendPost(participant.commitUrl, 5000)
  );
  let prepareResults;
  try {
    prepareResults = await Promise.all(preparePromises);
  } catch (error) {
    // A request failed (e.g., timed out), treat as prepare failure.
    prepareResults = [];
  }
  const allPrepared =
    prepareResults.length === participants.length &&
    prepareResults.every((status) => status === 200);

  if (allPrepared) {
    // Phase 2: Commit Phase
    try {
      const commitPromises = participants.map((participant) =>
        postWithRetry(participant.commitUrl, 3, 100)
      );
      await Promise.all(commitPromises);
      return true;
    } catch (error) {
      // If commit phase fails, attempt rollback on all participants.
      const rollbackPromises = participants.map((participant) =>
        postWithRetry(participant.rollbackUrl, 3, 100)
      );
      try {
        await Promise.all(rollbackPromises);
      } catch (err) {
        // Even if rollback fails, we return false.
      }
      return false;
    }
  } else {
    // Prepare phase failed: Rollback Phase
    const rollbackPromises = participants.map((participant) =>
      postWithRetry(participant.rollbackUrl, 3, 100)
    );
    try {
      await Promise.all(rollbackPromises);
    } catch (err) {
      // Even if rollback fails, we return false.
    }
    return false;
  }
}

module.exports = {
  coordinateTransaction,
  sendPost,
  postWithRetry,
};