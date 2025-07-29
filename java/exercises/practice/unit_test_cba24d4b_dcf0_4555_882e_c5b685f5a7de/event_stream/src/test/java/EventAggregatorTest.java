import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.RepeatedTest;
import org.junit.jupiter.api.Timeout;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;

public class EventAggregatorTest {

    private EventAggregator aggregator;

    // Assumes that the user implementation has a default constructor.
    @BeforeEach
    public void setup() {
        // Replace "EventAggregatorImpl" with the actual implementation class name.
        aggregator = new EventAggregatorImpl();
    }

    @Test
    public void testSingleEventInsertion() {
        long currentTime = System.currentTimeMillis();
        Event event = new Event(currentTime, "login");
        aggregator.recordEvent(event);
        long count = aggregator.getEventCount("login", currentTime, currentTime);
        assertEquals(1, count, "Expected count for single recorded event is 1");
    }

    @Test
    public void testMultipleEventInsertionDifferentTypes() {
        long baseTime = System.currentTimeMillis();
        // Record events of different types at varying timestamps
        Event e1 = new Event(baseTime, "login");
        Event e2 = new Event(baseTime + 100, "logout");
        Event e3 = new Event(baseTime + 200, "login");
        aggregator.recordEvent(e1);
        aggregator.recordEvent(e2);
        aggregator.recordEvent(e3);

        long loginCount = aggregator.getEventCount("login", baseTime, baseTime + 300);
        long logoutCount = aggregator.getEventCount("logout", baseTime, baseTime + 300);
        assertEquals(2, loginCount, "Expected count for login events is 2");
        assertEquals(1, logoutCount, "Expected count for logout events is 1");
    }

    @Test
    public void testQueryWithNoMatchingEventType() {
        long baseTime = System.currentTimeMillis();
        Event event = new Event(baseTime, "purchase");
        aggregator.recordEvent(event);
        long count = aggregator.getEventCount("nonexistent", baseTime, baseTime + 1000);
        assertEquals(0, count, "Expected count for nonexistent event type is 0");
    }

    @Test
    public void testInvalidTimeRangeThrowsException() {
        long baseTime = System.currentTimeMillis();
        IllegalArgumentException thrown = assertThrows(IllegalArgumentException.class, () -> {
            aggregator.getEventCount("login", baseTime + 1000, baseTime);
        });
        assertNotNull(thrown, "Expected IllegalArgumentException when startTime > endTime");
    }

    @Test
    @Timeout(5)
    public void testConcurrentRecording() throws InterruptedException, ExecutionException {
        int threadCount = 10;
        int eventsPerThread = 1000;
        ExecutorService executorService = Executors.newFixedThreadPool(threadCount);

        long baseTime = System.currentTimeMillis();
        List<Callable<Void>> tasks = new ArrayList<>();

        for (int i = 0; i < threadCount; i++) {
            tasks.add(() -> {
                for (int j = 0; j < eventsPerThread; j++) {
                    // Distribute timestamps within a one second interval
                    long eventTime = baseTime + ThreadLocalRandom.current().nextInt(0, 1000);
                    aggregator.recordEvent(new Event(eventTime, "click"));
                }
                return null;
            });
        }
        List<Future<Void>> futures = executorService.invokeAll(tasks);
        for (Future<Void> f : futures) {
            f.get();
        }
        executorService.shutdown();

        // Query the aggregator for the total number of 'click' events
        long totalClicks = aggregator.getEventCount("click", baseTime, baseTime + 1000);
        assertEquals(threadCount * eventsPerThread, totalClicks, "Expected total count of click events doesn't match");
    }

    @Test
    public void testEventsAtBoundaryTimes() {
        long baseTime = System.currentTimeMillis();
        // Record events exactly at the boundaries.
        Event eventStart = new Event(baseTime, "boundary");
        Event eventMiddle = new Event(baseTime + 500, "boundary");
        Event eventEnd = new Event(baseTime + 1000, "boundary");

        aggregator.recordEvent(eventStart);
        aggregator.recordEvent(eventMiddle);
        aggregator.recordEvent(eventEnd);

        // Query including the boundaries
        long countInclusive = aggregator.getEventCount("boundary", baseTime, baseTime + 1000);
        assertEquals(3, countInclusive, "Expected count including boundary events is 3");

        // Query excluding the first boundary
        long countExclusiveStart = aggregator.getEventCount("boundary", baseTime + 1, baseTime + 1000);
        assertEquals(2, countExclusiveStart, "Expected count excluding the start boundary is 2");

        // Query excluding the end boundary
        long countExclusiveEnd = aggregator.getEventCount("boundary", baseTime, baseTime + 999);
        assertEquals(2, countExclusiveEnd, "Expected count excluding the end boundary is 2");
    }

    @Test
    public void testRetentionPurgingSimulation() throws InterruptedException {
        // This test assumes that the implementation supports retention purging mechanism.
        // The retention period should be configurable, so we simulate the purging mechanism.
        long currentTime = System.currentTimeMillis();
        long retentionPeriodMillis = 1000; // For test, set retention to 1 second if supported.

        // Record an event older than the retention period
        Event oldEvent = new Event(currentTime - 2000, "old");
        aggregator.recordEvent(oldEvent);

        // Record a current event
        Event newEvent = new Event(currentTime, "old");
        aggregator.recordEvent(newEvent);

        // Depending on the purging implementation, after a delay the old event should be purged
        // Wait enough time to allow purging to occur. This depends on the implementation.
        Thread.sleep(1500);

        long count = aggregator.getEventCount("old", currentTime - 3000, currentTime + 1000);
        // We expect that only the new event remains.
        assertEquals(1, count, "After purging, expected only the new event to remain");
    }

    @Test
    public void testComplexQueryScenario() {
        // This test simulates a scenario with events of multiple types and verifies counts on overlapping ranges.
        long baseTime = System.currentTimeMillis();
        // Insert events for multiple types across a timeline
        for (int i = 0; i < 100; i++) {
            long timestamp = baseTime + i * 10;
            aggregator.recordEvent(new Event(timestamp, "A"));
            aggregator.recordEvent(new Event(timestamp, "B"));
            // Add extra event for type A every 5 iterations
            if (i % 5 == 0) {
                aggregator.recordEvent(new Event(timestamp, "A"));
            }
        }
        // Query different time ranges
        long countAFull = aggregator.getEventCount("A", baseTime, baseTime + 1000);
        long countBFull = aggregator.getEventCount("B", baseTime, baseTime + 1000);
        // For type A: 100 + (100/5) extra events = 100 + 20 = 120
        assertEquals(120, countAFull, "Expected count for type A events over full range is 120");
        // For type B: 100 events
        assertEquals(100, countBFull, "Expected count for type B events over full range is 100");

        // Query a subrange that starts later in the timeline
        long countASub = aggregator.getEventCount("A", baseTime + 300, baseTime + 700);
        // Count how many events for type A occur in this time range (estimate using the loop criteria)
        // Since events are inserted every 10ms, there are approximately 41 time slots.
        assertTrue(countASub > 0, "Expected non-zero count for type A in subrange");
    }
}