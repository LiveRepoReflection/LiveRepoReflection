import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.Set;
import java.util.HashSet;
import java.util.List;
import java.util.Arrays;

public class EventSchedulerTest {

    private EventScheduler scheduler;

    @BeforeEach
    public void setUp() {
        scheduler = new EventScheduler();
    }

    @Test
    public void testScheduleSuccess() {
        Set<String> resources = new HashSet<>(Arrays.asList("CPU-1", "Database-A"));
        EventScheduler.ScheduleResult result = scheduler.scheduleEvent("E1", 1000L, 2000L, 5, resources);
        assertTrue(result.isSuccess());
        assertTrue(result.getConflictingEvents().isEmpty());
    }

    @Test
    public void testScheduleConflict() {
        Set<String> resources1 = new HashSet<>(Arrays.asList("CPU-1", "Database-A"));
        EventScheduler.ScheduleResult result1 = scheduler.scheduleEvent("E1", 1000L, 2000L, 5, resources1);
        assertTrue(result1.isSuccess());

        Set<String> resources2 = new HashSet<>(Arrays.asList("CPU-1"));
        EventScheduler.ScheduleResult result2 = scheduler.scheduleEvent("E2", 1500L, 2500L, 4, resources2);
        assertFalse(result2.isSuccess());
        assertTrue(result2.getConflictingEvents().contains("E1"));
    }

    @Test
    public void testCancelEvent() {
        Set<String> resources = new HashSet<>(Arrays.asList("CPU-1", "Database-A"));
        EventScheduler.ScheduleResult result = scheduler.scheduleEvent("E1", 1000L, 2000L, 5, resources);
        assertTrue(result.isSuccess());

        boolean cancelled = scheduler.cancelEvent("E1");
        assertTrue(cancelled);

        Set<String> newResources = new HashSet<>(Arrays.asList("CPU-1"));
        EventScheduler.ScheduleResult resultAfterCancel = scheduler.scheduleEvent("E2", 1500L, 2500L, 4, newResources);
        assertTrue(resultAfterCancel.isSuccess());
    }

    @Test
    public void testQueryEvents() {
        Set<String> r1 = new HashSet<>(Arrays.asList("CPU-1"));
        scheduler.scheduleEvent("E1", 1000L, 2000L, 3, r1);
        scheduler.scheduleEvent("E2", 900L, 1800L, 5, new HashSet<>(Arrays.asList("Database-A")));
        scheduler.scheduleEvent("E3", 1100L, 2100L, 5, new HashSet<>(Arrays.asList("MeetingRoom-1")));

        List<String> queryResult = scheduler.queryEvents(800L, 2200L);
        assertEquals(3, queryResult.size());
        assertEquals("E2", queryResult.get(0));
        assertEquals("E3", queryResult.get(1));
        assertEquals("E1", queryResult.get(2));
    }

    @Test
    public void testOptimizeResources() {
        scheduler.scheduleEvent("E1", 1000L, 2000L, 2, new HashSet<>(Arrays.asList("CPU-1")));
        scheduler.scheduleEvent("E2", 1500L, 2500L, 3, new HashSet<>(Arrays.asList("MeetingRoom-1")));

        Set<String> newResources = new HashSet<>(Arrays.asList("CPU-1", "MeetingRoom-1"));
        List<String> optimizeSet = scheduler.optimizeResources(1200L, 2300L, 5, newResources);
        assertEquals(2, optimizeSet.size());
        assertTrue(optimizeSet.contains("E1"));
        assertTrue(optimizeSet.contains("E2"));
    }

    @Test
    public void testNonConflictingOverlappingEvents() {
        scheduler.scheduleEvent("E1", 1000L, 2000L, 4, new HashSet<>(Arrays.asList("CPU-1")));
        scheduler.scheduleEvent("E2", 1500L, 2500L, 4, new HashSet<>(Arrays.asList("Database-A")));
        List<String> queryResult = scheduler.queryEvents(900L, 2600L);
        assertEquals(2, queryResult.size());
        assertTrue(queryResult.contains("E1"));
        assertTrue(queryResult.contains("E2"));
    }
}