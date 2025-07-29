import java.util.NavigableMap;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentSkipListMap;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class EventAggregatorImpl implements EventAggregator {

    private final ConcurrentHashMap<String, ConcurrentSkipListMap<Long, AtomicInteger>> eventMap;
    private final ScheduledExecutorService scheduler;
    private final long retentionPeriodMillis;

    public EventAggregatorImpl() {
        // Default retention period set to 1000ms for testing purposes.
        this.retentionPeriodMillis = 1000;
        this.eventMap = new ConcurrentHashMap<>();
        this.scheduler = Executors.newSingleThreadScheduledExecutor();
        startRetentionTask();
    }

    private void startRetentionTask() {
        scheduler.scheduleAtFixedRate(new Runnable() {
            @Override
            public void run() {
                purgeOldEvents();
            }
        }, retentionPeriodMillis, retentionPeriodMillis, TimeUnit.MILLISECONDS);
    }

    private void purgeOldEvents() {
        long threshold = System.currentTimeMillis() - retentionPeriodMillis;
        for (ConcurrentSkipListMap<Long, AtomicInteger> map : eventMap.values()) {
            NavigableMap<Long, AtomicInteger> headMap = map.headMap(threshold, false);
            headMap.clear();
        }
    }

    @Override
    public void recordEvent(Event event) {
        if (event == null || event.type == null) {
            throw new IllegalArgumentException("Invalid event");
        }
        ConcurrentSkipListMap<Long, AtomicInteger> typeMap = eventMap.computeIfAbsent(event.type,
                key -> new ConcurrentSkipListMap<>());
        typeMap.compute(event.timestamp, (k, v) -> {
            if (v == null) {
                return new AtomicInteger(1);
            } else {
                v.incrementAndGet();
                return v;
            }
        });
    }

    @Override
    public long getEventCount(String eventType, long startTime, long endTime) {
        if (eventType == null) {
            throw new IllegalArgumentException("Event type cannot be null");
        }
        if (startTime > endTime) {
            throw new IllegalArgumentException("startTime cannot be greater than endTime");
        }
        ConcurrentSkipListMap<Long, AtomicInteger> typeMap = eventMap.get(eventType);
        if (typeMap == null) {
            return 0;
        }
        NavigableMap<Long, AtomicInteger> subMap = typeMap.subMap(startTime, true, endTime, true);
        long count = 0;
        for (AtomicInteger value : subMap.values()) {
            count += value.get();
        }
        return count;
    }

    // Shutdown method for testing and cleanup.
    public void shutdown() {
        scheduler.shutdownNow();
    }
}