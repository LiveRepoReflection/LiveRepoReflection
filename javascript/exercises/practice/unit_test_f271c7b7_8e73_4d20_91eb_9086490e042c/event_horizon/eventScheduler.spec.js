const { scheduleEvent, cancelEvent, retrieveEvents, triggerEvents, _resetStore } = require('./eventScheduler');

// Mock notifyUser function which is assumed to exist in the implementation.
const notifyUser = jest.fn();

// Inject the mock notifyUser into our event scheduler module if the module supports dependency injection.
if (typeof global.notifyUser === 'undefined') {
  global.notifyUser = notifyUser;
}

describe('Event Scheduler', () => {
  // Reset the in-memory store before each test to ensure isolation.
  beforeEach(() => {
    jest.useFakeTimers();
    notifyUser.mockClear();
    // _resetStore is an assumed helper function that resets the internal event store.
    _resetStore();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('should schedule an event and retrieve it for a participant', () => {
    const event = {
      id: 'evt1',
      timestamp: Date.now() + 60000, // event scheduled 60 seconds in the future
      payload: { message: 'Meeting at 3 PM' },
      participants: ['userA', 'userB']
    };

    scheduleEvent(event);

    const retrievedForUserA = retrieveEvents('userA', Date.now(), Date.now() + 120000);
    expect(retrievedForUserA).toHaveLength(1);
    expect(retrievedForUserA[0].id).toBe('evt1');

    const retrievedForUserB = retrieveEvents('userB', Date.now(), Date.now() + 120000);
    expect(retrievedForUserB).toHaveLength(1);
    expect(retrievedForUserB[0].id).toBe('evt1');
  });

  test('should cancel a scheduled event so it will not be retrieved or triggered', () => {
    const event = {
      id: 'evt2',
      timestamp: Date.now() + 30000,
      payload: { message: 'Lunch at noon' },
      participants: ['userC']
    };

    scheduleEvent(event);
    cancelEvent(event.id);

    const retrieved = retrieveEvents('userC', Date.now(), Date.now() + 60000);
    expect(retrieved).toHaveLength(0);

    // Fast-forward timers to ensure triggering phase runs
    jest.advanceTimersByTime(60000);
    triggerEvents();
    expect(notifyUser).not.toHaveBeenCalled();
  });

  test('should trigger events whose timestamp has passed and notify all participants', () => {
    const currentTime = Date.now();
    const event = {
      id: 'evt3',
      timestamp: currentTime - 1000, // event scheduled in the past
      payload: { message: 'Past Event' },
      participants: ['userD', 'userE']
    };

    scheduleEvent(event);
    triggerEvents();

    // Verify notifyUser is called for all participants
    expect(notifyUser).toHaveBeenCalledTimes(2);
    expect(notifyUser).toHaveBeenCalledWith('userD', event.payload);
    expect(notifyUser).toHaveBeenCalledWith('userE', event.payload);

    // After triggering, the event should be removed from the store
    const retrieved = retrieveEvents('userD', 0, Date.now() + 10000);
    expect(retrieved).toHaveLength(0);
  });

  test('should only trigger events once even if triggerEvents is called multiple times', () => {
    const event = {
      id: 'evt4',
      timestamp: Date.now() - 500,
      payload: { message: 'One-time Event' },
      participants: ['userF']
    };

    scheduleEvent(event);
    triggerEvents();
    triggerEvents();
    expect(notifyUser).toHaveBeenCalledTimes(1);
    expect(notifyUser).toHaveBeenCalledWith('userF', event.payload);
  });

  test('should retrieve only events within the specified time range and sorted by timestamp', () => {
    const now = Date.now();
    const events = [
      { id: 'evt5', timestamp: now + 10000, payload: { data: 1 }, participants: ['userG'] },
      { id: 'evt6', timestamp: now + 5000, payload: { data: 2 }, participants: ['userG'] },
      { id: 'evt7', timestamp: now + 15000, payload: { data: 3 }, participants: ['userG'] },
      { id: 'evt8', timestamp: now + 20000, payload: { data: 4 }, participants: ['userG'] }
    ];

    events.forEach(event => scheduleEvent(event));

    const retrieved = retrieveEvents('userG', now, now + 16000);
    expect(retrieved).toHaveLength(3);
    // They should be sorted in ascending order by timestamp.
    expect(retrieved[0].id).toBe('evt6');
    expect(retrieved[1].id).toBe('evt5');
    expect(retrieved[2].id).toBe('evt7');
  });

  test('should handle concurrent scheduling and cancellation correctly', () => {
    const eventA = {
      id: 'evt9',
      timestamp: Date.now() + 20000,
      payload: { info: 'Concurrent Test A' },
      participants: ['userH']
    };
    const eventB = {
      id: 'evt10',
      timestamp: Date.now() + 20000,
      payload: { info: 'Concurrent Test B' },
      participants: ['userH']
    };

    // Simulate concurrent scheduling.
    scheduleEvent(eventA);
    scheduleEvent(eventB);

    // Concurrent cancellation of one event.
    cancelEvent(eventA.id);

    const retrieved = retrieveEvents('userH', Date.now(), Date.now() + 30000);
    expect(retrieved).toHaveLength(1);
    expect(retrieved[0].id).toBe('evt10');
  });

  test('should not trigger events if notification fails on one participant, ensuring idempotency on next trigger', () => {
    // To simulate a failure, override notifyUser temporarily.
    const originalNotify = global.notifyUser;
    let callCount = 0;
    global.notifyUser = jest.fn((participantId, payload) => {
      callCount++;
      // Simulate failure for the first call only.
      if (callCount === 1) {
        throw new Error('Notification failure');
      }
    });

    const event = {
      id: 'evt11',
      timestamp: Date.now() - 2000,
      payload: { errorTest: true },
      participants: ['userI', 'userJ']
    };

    scheduleEvent(event);

    // First trigger attempt: one notification fails.
    try {
      triggerEvents();
    } catch (e) {
      // Expected error from notification failure.
    }
    // The event should still be present because not all notifications succeeded.
    let retrieved = retrieveEvents('userI', 0, Date.now() + 10000);
    expect(retrieved).toHaveLength(1);

    // Replace notifyUser with a successful mock and trigger again.
    global.notifyUser = jest.fn();
    triggerEvents();
    retrieved = retrieveEvents('userI', 0, Date.now() + 10000);
    expect(retrieved).toHaveLength(0);
    expect(global.notifyUser).toHaveBeenCalledTimes(2);
    expect(global.notifyUser).toHaveBeenCalledWith('userI', event.payload);
    expect(global.notifyUser).toHaveBeenCalledWith('userJ', event.payload);

    // Restore notifyUser.
    global.notifyUser = originalNotify;
  });
});