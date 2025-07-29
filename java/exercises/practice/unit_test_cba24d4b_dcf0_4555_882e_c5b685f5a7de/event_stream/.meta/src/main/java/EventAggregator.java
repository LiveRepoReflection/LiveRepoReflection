public interface EventAggregator {
    void recordEvent(Event event);
    long getEventCount(String eventType, long startTime, long endTime);
}