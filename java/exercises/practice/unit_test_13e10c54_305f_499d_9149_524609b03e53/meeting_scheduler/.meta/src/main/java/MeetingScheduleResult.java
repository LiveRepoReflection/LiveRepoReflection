import java.time.LocalDateTime;

public class MeetingScheduleResult {
    private final LocalDateTime meetingStartTime;
    private final int roomCapacity;

    public MeetingScheduleResult(LocalDateTime meetingStartTime, int roomCapacity) {
        this.meetingStartTime = meetingStartTime;
        this.roomCapacity = roomCapacity;
    }

    public LocalDateTime getMeetingStartTime() {
        return meetingStartTime;
    }

    public int getRoomCapacity() {
        return roomCapacity;
    }
}