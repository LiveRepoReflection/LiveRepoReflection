const http = require('http');
const { coordinateTransaction } = require('./distributed_tx');

jest.setTimeout(15000);

function createTestService(options = {}) {
  let commitCount = 0;
  let rollbackCount = 0;
  const server = http.createServer((req, res) => {
    if (req.method !== 'POST') {
      res.statusCode = 405;
      res.end();
      return;
    }
    if (req.url === '/commit') {
      commitCount++;
      if (options.commitHandler) {
        return options.commitHandler(req, res, commitCount);
      } else {
        res.statusCode = 200;
        res.end();
      }
    } else if (req.url === '/rollback') {
      rollbackCount++;
      if (options.rollbackHandler) {
        return options.rollbackHandler(req, res, rollbackCount);
      } else {
        res.statusCode = 200;
        res.end();
      }
    } else {
      res.statusCode = 404;
      res.end();
    }
  });
  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => {
      const port = server.address().port;
      const commitUrl = `http://127.0.0.1:${port}/commit`;
      const rollbackUrl = `http://127.0.0.1:${port}/rollback`;
      resolve({
        server,
        commitUrl,
        rollbackUrl,
        getCommitCount: () => commitCount,
        getRollbackCount: () => rollbackCount,
        close: () =>
          new Promise((resClose) => {
            server.close(() => resClose());
          }),
      });
    });
  });
}

describe('coordinateTransaction', () => {
  test('successful transaction commits', async () => {
    // Two services that always succeed in prepare and commit.
    const service1 = await createTestService();
    const service2 = await createTestService();

    const participants = [
      {
        serviceName: 'Service1',
        commitUrl: service1.commitUrl,
        rollbackUrl: service1.rollbackUrl,
        roleName: 'role1',
      },
      {
        serviceName: 'Service2',
        commitUrl: service2.commitUrl,
        rollbackUrl: service2.rollbackUrl,
        roleName: 'role2',
      },
    ];

    const result = await coordinateTransaction(participants);
    expect(result).toBe(true);
    // Expect two calls per service (prepare + commit)
    expect(service1.getCommitCount()).toBe(2);
    expect(service2.getCommitCount()).toBe(2);
    // Rollback should not be called
    expect(service1.getRollbackCount()).toBe(0);
    expect(service2.getRollbackCount()).toBe(0);

    await service1.close();
    await service2.close();
  });

  test('prepare phase failure triggers rollback', async () => {
    // Service that fails prepare with 409 Conflict
    const failingService = await createTestService({
      commitHandler: (req, res) => {
        res.statusCode = 409;
        res.end();
      },
    });
    // Normal service
    const normalService = await createTestService();

    const participants = [
      {
        serviceName: 'FailingService',
        commitUrl: failingService.commitUrl,
        rollbackUrl: failingService.rollbackUrl,
        roleName: 'roleFail',
      },
      {
        serviceName: 'NormalService',
        commitUrl: normalService.commitUrl,
        rollbackUrl: normalService.rollbackUrl,
        roleName: 'roleNormal',
      },
    ];

    const result = await coordinateTransaction(participants);
    expect(result).toBe(false);
    // Both services received one prepare call each.
    expect(failingService.getCommitCount()).toBe(1);
    expect(normalService.getCommitCount()).toBe(1);
    // Both should have executed rollback.
    expect(failingService.getRollbackCount()).toBe(1);
    expect(normalService.getRollbackCount()).toBe(1);

    await failingService.close();
    await normalService.close();
  });

  test('rollback retry on failure eventually succeeds', async () => {
    // Service that fails prepare to trigger rollback.
    const retryService = await createTestService({
      commitHandler: (req, res) => {
        // Fail prepare with 409 Conflict
        res.statusCode = 409;
        res.end();
      },
      rollbackHandler: (req, res, callCount) => {
        // Fail first two rollback attempts with 500, then succeed.
        if (callCount < 3) {
          res.statusCode = 500;
          res.end();
        } else {
          res.statusCode = 200;
          res.end();
        }
      },
    });
    // Normal service that responds normally.
    const normalService = await createTestService();

    const participants = [
      {
        serviceName: 'RetryService',
        commitUrl: retryService.commitUrl,
        rollbackUrl: retryService.rollbackUrl,
        roleName: 'retryRole',
      },
      {
        serviceName: 'NormalService',
        commitUrl: normalService.commitUrl,
        rollbackUrl: normalService.rollbackUrl,
        roleName: 'normalRole',
      },
    ];

    const result = await coordinateTransaction(participants);
    expect(result).toBe(false);
    // Both got one prepare call each.
    expect(retryService.getCommitCount()).toBe(1);
    expect(normalService.getCommitCount()).toBe(1);
    // Normal service should perform rollback once.
    expect(normalService.getRollbackCount()).toBe(1);
    // Retry service rollback should have been retried (at least 3 attempts)
    expect(retryService.getRollbackCount()).toBeGreaterThanOrEqual(3);

    await retryService.close();
    await normalService.close();
  });

  test('prepare timeout triggers rollback', async () => {
    // Service that simulates a timeout in prepare by delaying response beyond timeout threshold
    const timeoutService = await createTestService({
      commitHandler: (req, res) => {
        // Delay response by 7000ms to simulate timeout
        setTimeout(() => {
          res.statusCode = 200;
          res.end();
        }, 7000);
      },
    });
    // Normal service
    const normalService = await createTestService();

    const participants = [
      {
        serviceName: 'TimeoutService',
        commitUrl: timeoutService.commitUrl,
        rollbackUrl: timeoutService.rollbackUrl,
        roleName: 'roleTimeout',
      },
      {
        serviceName: 'NormalService',
        commitUrl: normalService.commitUrl,
        rollbackUrl: normalService.rollbackUrl,
        roleName: 'roleNormal',
      },
    ];

    const result = await coordinateTransaction(participants);
    expect(result).toBe(false);
    // The timeout service should have one commit call (that will timeout and be counted as error)
    expect(timeoutService.getCommitCount()).toBe(1);
    expect(normalService.getCommitCount()).toBe(1);
    // Rollback should be triggered for both services.
    expect(timeoutService.getRollbackCount()).toBe(1);
    expect(normalService.getRollbackCount()).toBe(1);

    await timeoutService.close();
    await normalService.close();
  });

  test('handles concurrent transactions correctly', async () => {
    // Create two pairs of services for two parallel transactions.
    const serviceA1 = await createTestService();
    const serviceA2 = await createTestService();
    const serviceB1 = await createTestService({
      commitHandler: (req, res) => {
        res.statusCode = 409;
        res.end();
      },
    });
    const serviceB2 = await createTestService();

    const participantsTxA = [
      {
        serviceName: 'ServiceA1',
        commitUrl: serviceA1.commitUrl,
        rollbackUrl: serviceA1.rollbackUrl,
        roleName: 'roleA1',
      },
      {
        serviceName: 'ServiceA2',
        commitUrl: serviceA2.commitUrl,
        rollbackUrl: serviceA2.rollbackUrl,
        roleName: 'roleA2',
      },
    ];
    const participantsTxB = [
      {
        serviceName: 'ServiceB1',
        commitUrl: serviceB1.commitUrl,
        rollbackUrl: serviceB1.rollbackUrl,
        roleName: 'roleB1',
      },
      {
        serviceName: 'ServiceB2',
        commitUrl: serviceB2.commitUrl,
        rollbackUrl: serviceB2.rollbackUrl,
        roleName: 'roleB2',
      },
    ];

    const [resultA, resultB] = await Promise.all([
      coordinateTransaction(participantsTxA),
      coordinateTransaction(participantsTxB),
    ]);
    expect(resultA).toBe(true);
    expect(resultB).toBe(false);

    // For transaction A, two commit calls per service.
    expect(serviceA1.getCommitCount()).toBe(2);
    expect(serviceA2.getCommitCount()).toBe(2);
    // For transaction B, both services got one commit call and one rollback call.
    expect(serviceB1.getCommitCount()).toBe(1);
    expect(serviceB2.getCommitCount()).toBe(1);
    expect(serviceB1.getRollbackCount()).toBe(1);
    expect(serviceB2.getRollbackCount()).toBe(1);

    await serviceA1.close();
    await serviceA2.close();
    await serviceB1.close();
    await serviceB2.close();
  });
});