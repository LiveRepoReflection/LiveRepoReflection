import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

public class MeetingScheduler {
    private final List<Integer> employees;
    private final int duration;
    private final LocalDateTime horizonStart;
    private final LocalDateTime horizonEnd;
    private final int minimumAttendance;
    private final List<Integer> rooms;
    private final Map<Integer, Map<String, Object>> employeeData;
    // Regular work hours constants
    private final int workStartHour = 9;
    private final int workEndHour = 17;
    // Penalty for scheduling outside regular hours
    private final int outsideHoursPenalty = 1000;

    public MeetingScheduler(List<Integer> employees, int duration,
                            LocalDateTime schedulingHorizonStart, LocalDateTime schedulingHorizonEnd,
                            int minimumAttendance, List<Integer> rooms,
                            Map<Integer, Map<String, Object>> employeeData) {
        this.employees = employees;
        this.duration = duration;
        this.horizonStart = schedulingHorizonStart;
        this.horizonEnd = schedulingHorizonEnd;
        this.minimumAttendance = minimumAttendance;
        this.rooms = new ArrayList<>(rooms);
        Collections.sort(this.rooms);
        this.employeeData = employeeData;
    }

    public MeetingScheduleResult scheduleMeeting() {
        LocalDateTime bestTime = null;
        int bestRoomCapacity = 0;
        double bestCost = Double.MAX_VALUE;

        // The latest candidate meeting start time is where meetingEnd <= horizonEnd.
        LocalDateTime candidateTime = horizonStart;
        while (!candidateTime.plusMinutes(duration).isAfter(horizonEnd)) {
            LocalDateTime candidateEnd = candidateTime.plusMinutes(duration);
            // For each employee, determine if they are busy in this candidate timeslot.
            int availableCount = 0;
            double busyPenalty = 0;
            List<Double> newBusyCounts = new ArrayList<>();
            for (Integer empId : employees) {
                Map<String, Object> empInfo = employeeData.get(empId);
                int meetingCost = (Integer) empInfo.get("meetingCost");
                @SuppressWarnings("unchecked")
                List<LocalDateTime[]> busySlots = (List<LocalDateTime[]>) empInfo.get("busySlots");
                boolean conflicting = false;
                for (LocalDateTime[] slot : busySlots) {
                    if (overlap(slot[0], slot[1], candidateTime, candidateEnd)) {
                        conflicting = true;
                        break;
                    }
                }
                // If not conflicting, employee can attend and will have meeting added as a new busy slot.
                if (!conflicting) {
                    availableCount++;
                    newBusyCounts.add(busySlots.size() + 1.0);
                } else {
                    // Employee is forced to attend even if busy; penalty incurred.
                    busyPenalty += meetingCost;
                    newBusyCounts.add((double) busySlots.size());
                }
            }

            // Verify minimum attendance requirement and room capacity.
            if (availableCount < minimumAttendance) {
                candidateTime = candidateTime.plusMinutes(1);
                continue;
            }

            // Determine smallest room that fits available employees.
            int selectedRoom = -1;
            for (Integer roomCap : rooms) {
                if (roomCap >= availableCount) {
                    selectedRoom = roomCap;
                    break;
                }
            }
            if (selectedRoom == -1) {
                candidateTime = candidateTime.plusMinutes(1);
                continue;
            }

            // Compute fairness variance: variance of new busy counts.
            double mean = 0;
            for (Double count : newBusyCounts) {
                mean += count;
            }
            mean /= newBusyCounts.size();

            double variance = 0;
            for (Double count : newBusyCounts) {
                variance += Math.pow(count - mean, 2);
            }
            variance /= newBusyCounts.size();

            // Penalty if meeting is outside regular hours.
            int hour = candidateTime.getHour();
            int minute = candidateTime.getMinute();
            int penalty = 0;
            if (hour < workStartHour || hour >= workEndHour) {
                penalty = outsideHoursPenalty;
            }

            double totalCost = busyPenalty + variance + penalty;
            // Choose candidate with minimal cost; tiebreaker: earliest start time.
            if (totalCost < bestCost) {
                bestCost = totalCost;
                bestTime = candidateTime;
                bestRoomCapacity = selectedRoom;
            }
            candidateTime = candidateTime.plusMinutes(1);
        }

        if (bestTime == null) {
            return null;
        }
        return new MeetingScheduleResult(bestTime, bestRoomCapacity);
    }

    private boolean overlap(LocalDateTime start1, LocalDateTime end1, LocalDateTime start2, LocalDateTime end2) {
        return start1.isBefore(end2) && start2.isBefore(end1);
    }
}