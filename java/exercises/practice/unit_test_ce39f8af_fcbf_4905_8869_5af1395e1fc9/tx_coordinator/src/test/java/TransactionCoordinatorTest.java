import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.Assertions;

import java.time.Duration;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

public class TransactionCoordinatorTest {

    @Test
    public void testAllParticipantsVoteCommit() {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        Set<String> participants = new HashSet<>();
        participants.add("ServiceA");
        participants.add("ServiceB");

        String transactionId = coordinator.beginTransaction(participants);

        Map<String, Function<String, String>> participantActions = new HashMap<>();
        participantActions.put("ServiceA", message -> {
            if ("prepare".equals(message)) {
                return "vote_commit";
            } else {
                return "ack";
            }
        });
        participantActions.put("ServiceB", message -> {
            if ("prepare".equals(message)) {
                return "vote_commit";
            } else {
                return "ack";
            }
        });

        TransactionCoordinator.TransactionResult result = coordinator.executeTransaction(transactionId, participantActions);
        Assertions.assertEquals(TransactionCoordinator.TransactionResult.COMMIT, result);
    }

    @Test
    public void testOneParticipantVotesRollback() {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        Set<String> participants = new HashSet<>();
        participants.add("ServiceA");
        participants.add("ServiceB");

        String transactionId = coordinator.beginTransaction(participants);

        Map<String, Function<String, String>> participantActions = new HashMap<>();
        // ServiceA votes commit
        participantActions.put("ServiceA", message -> {
            if ("prepare".equals(message)) {
                return "vote_commit";
            } else {
                return "ack";
            }
        });
        // ServiceB votes rollback
        participantActions.put("ServiceB", message -> {
            if ("prepare".equals(message)) {
                return "vote_rollback";
            } else {
                return "ack";
            }
        });

        TransactionCoordinator.TransactionResult result = coordinator.executeTransaction(transactionId, participantActions);
        Assertions.assertEquals(TransactionCoordinator.TransactionResult.ROLLBACK, result);
    }

    @Test
    public void testExceptionDuringPreparePhase() {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        Set<String> participants = new HashSet<>();
        participants.add("ServiceA");
        participants.add("ServiceB");

        String transactionId = coordinator.beginTransaction(participants);

        Map<String, Function<String, String>> participantActions = new HashMap<>();
        // ServiceA votes commit
        participantActions.put("ServiceA", message -> {
            if ("prepare".equals(message)) {
                return "vote_commit";
            } else {
                return "ack";
            }
        });
        // ServiceB throws an exception during prepare phase
        participantActions.put("ServiceB", message -> {
            if ("prepare".equals(message)) {
                throw new RuntimeException("Simulated exception");
            } else {
                return "ack";
            }
        });

        TransactionCoordinator.TransactionResult result = coordinator.executeTransaction(transactionId, participantActions);
        Assertions.assertEquals(TransactionCoordinator.TransactionResult.ROLLBACK, result);
    }

    @Test
    @Timeout(value = 10, unit = TimeUnit.SECONDS)
    public void testParticipantTimeout() {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        Set<String> participants = new HashSet<>();
        participants.add("ServiceA");
        participants.add("ServiceB");

        String transactionId = coordinator.beginTransaction(participants);

        Map<String, Function<String, String>> participantActions = new HashMap<>();
        // ServiceA behaves normally
        participantActions.put("ServiceA", message -> {
            if ("prepare".equals(message)) {
                return "vote_commit";
            } else {
                return "ack";
            }
        });
        // ServiceB simulates timeout by sleeping longer than the coordinator's timeout (5 seconds)
        participantActions.put("ServiceB", message -> {
            if ("prepare".equals(message)) {
                try {
                    Thread.sleep(6000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                return "vote_commit";
            } else {
                return "ack";
            }
        });

        TransactionCoordinator.TransactionResult result = coordinator.executeTransaction(transactionId, participantActions);
        Assertions.assertEquals(TransactionCoordinator.TransactionResult.ROLLBACK, result);
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        ExecutorService executor = Executors.newFixedThreadPool(4);
        int transactionCount = 10;
        Map<Integer, TransactionCoordinator.TransactionResult> results = Collections.synchronizedMap(new HashMap<>());

        for (int i = 0; i < transactionCount; i++) {
            final int txNumber = i;
            executor.submit(() -> {
                Set<String> participants = new HashSet<>();
                participants.add("ServiceA_" + txNumber);
                participants.add("ServiceB_" + txNumber);
                String transactionId = coordinator.beginTransaction(participants);

                Map<String, Function<String, String>> participantActions = new HashMap<>();
                // Both participants vote commit
                participantActions.put("ServiceA_" + txNumber, message -> {
                    if ("prepare".equals(message)) {
                        return "vote_commit";
                    } else {
                        return "ack";
                    }
                });
                participantActions.put("ServiceB_" + txNumber, message -> {
                    if ("prepare".equals(message)) {
                        return "vote_commit";
                    } else {
                        return "ack";
                    }
                });

                TransactionCoordinator.TransactionResult result = coordinator.executeTransaction(transactionId, participantActions);
                results.put(txNumber, result);
            });
        }
        executor.shutdown();
        executor.awaitTermination(15, TimeUnit.SECONDS);

        for (int i = 0; i < transactionCount; i++) {
            Assertions.assertEquals(TransactionCoordinator.TransactionResult.COMMIT, results.get(i));
        }
    }
}