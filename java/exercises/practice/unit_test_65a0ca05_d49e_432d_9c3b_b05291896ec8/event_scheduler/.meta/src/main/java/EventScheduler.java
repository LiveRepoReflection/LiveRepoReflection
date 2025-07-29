import java.util.Map;
import java.util.HashMap;
import java.util.Set;
import java.util.HashSet;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;

public class EventScheduler {

    private Map<String, Event> events;

    public EventScheduler() {
        events = new HashMap<>();
    }

    // Inner class representing an event
    private static class Event {
        String id;
        long start;
        long end;
        int priority;
        Set<String> resources;

        Event(String id, long start, long end, int priority, Set<String> resources) {
            this.id = id;
            this.start = start;
            this.end = end;
            this.priority = priority;
            this.resources = new HashSet<>(resources);
        }

        // Check if the event time overlaps with the given time range
        boolean overlaps(long queryStart, long queryEnd) {
            return this.end >= queryStart && this.start <= queryEnd;
        }

        // Check if resources overlap with the provided resource set
        boolean hasResourceConflict(Set<String> otherResources) {
            for (String res : resources) {
                if (otherResources.contains(res)) {
                    return true;
                }
            }
            return false;
        }
    }

    // Class representing the result of scheduling an event
    public static class ScheduleResult {
        private final boolean success;
        private final List<String> conflictingEvents;

        public ScheduleResult(boolean success, List<String> conflictingEvents) {
            this.success = success;
            this.conflictingEvents = new ArrayList<>(conflictingEvents);
        }

        public boolean isSuccess() {
            return success;
        }

        public List<String> getConflictingEvents() {
            return new ArrayList<>(conflictingEvents);
        }
    }

    /**
     * Schedule an event if possible.
     * @param eventId Unique event ID.
     * @param start Start time in epoch milliseconds.
     * @param end End time in epoch milliseconds.
     * @param priority Higher integer means higher priority.
     * @param resources Set of required resource identifiers.
     * @return ScheduleResult indicating success or failure and list of conflicting event IDs if conflict occurs.
     */
    public synchronized ScheduleResult scheduleEvent(String eventId, long start, long end, int priority, Set<String> resources) {
        if (events.containsKey(eventId)) {
            // Duplicate event id is not allowed
            List<String> conflict = new ArrayList<>();
            conflict.add(eventId);
            return new ScheduleResult(false, conflict);
        }

        List<String> conflicts = new ArrayList<>();
        // Check for resource conflicts with overlapping events.
        for (Event e : events.values()) {
            if (e.overlaps(start, end) && e.hasResourceConflict(resources)) {
                conflicts.add(e.id);
            }
        }
        if (!conflicts.isEmpty()) {
            return new ScheduleResult(false, conflicts);
        }
        // No conflict, so schedule the event.
        Event newEvent = new Event(eventId, start, end, priority, resources);
        events.put(eventId, newEvent);
        return new ScheduleResult(true, Collections.emptyList());
    }

    /**
     * Cancel an event.
     * @param eventId Unique event ID to cancel.
     * @return true if the event was cancelled, false if event not found.
     */
    public synchronized boolean cancelEvent(String eventId) {
        if (events.containsKey(eventId)) {
            events.remove(eventId);
            return true;
        }
        return false;
    }

    /**
     * Query events that overlap with a given time range.
     * Sorted by priority descending and then by start time ascending.
     * @param queryStart Start time of the query range.
     * @param queryEnd End time of the query range.
     * @return List of event IDs.
     */
    public synchronized List<String> queryEvents(long queryStart, long queryEnd) {
        List<Event> result = new ArrayList<>();
        for (Event e : events.values()) {
            if (e.overlaps(queryStart, queryEnd)) {
                result.add(e);
            }
        }
        // Sort first by descending priority, then ascending start time.
        result.sort(new Comparator<Event>() {
            @Override
            public int compare(Event e1, Event e2) {
                if (e2.priority != e1.priority) {
                    return Integer.compare(e2.priority, e1.priority);
                }
                return Long.compare(e1.start, e2.start);
            }
        });
        List<String> ids = new ArrayList<>();
        for (Event e : result) {
            ids.add(e.id);
        }
        return ids;
    }

    /**
     * Optimize resource usage for a new event by suggesting the minimal set of lower-priority events to cancel.
     * The new event can be scheduled only if all conflicting events (that share a resource and overlap in time)
     * with lower priority are cancelled. If any conflicting event with equal or higher priority exists, return an empty list.
     * @param start Start time of the new event.
     * @param end End time of the new event.
     * @param newPriority Priority of the new event.
     * @param newResources Resource requirements of the new event.
     * @return List of event IDs representing the minimal set to cancel, or an empty list if not possible.
     */
    public synchronized List<String> optimizeResources(long start, long end, int newPriority, Set<String> newResources) {
        List<String> toCancel = new ArrayList<>();
        for (Event e : events.values()) {
            if (e.overlaps(start, end) && e.hasResourceConflict(newResources)) {
                if (e.priority >= newPriority) {
                    // Cannot preempt events with equal or higher priority.
                    return new ArrayList<>();
                } else {
                    toCancel.add(e.id);
                }
            }
        }
        // In this simplified model, the minimal set is simply all conflicting lower-priority events.
        // More advanced algorithms might consider trade-offs, but here this is sufficient.
        return toCancel;
    }
}