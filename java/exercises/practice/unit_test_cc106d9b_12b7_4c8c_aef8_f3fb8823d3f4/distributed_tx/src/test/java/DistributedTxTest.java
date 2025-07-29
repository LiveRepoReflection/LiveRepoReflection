import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class DistributedTxTest {

    @Mock
    private Participant participant1;
    @Mock
    private Participant participant2;
    @Mock
    private Participant participant3;

    private Coordinator coordinator;
    private Transaction transaction;

    @BeforeEach
    void setUp() {
        coordinator = new Coordinator();
        transaction = new Transaction("TX1");
    }

    @Test
    void testSuccessfulTransaction() throws Exception {
        // Setup participants to vote commit
        when(participant1.prepare(transaction)).thenReturn(Vote.COMMIT);
        when(participant2.prepare(transaction)).thenReturn(Vote.COMMIT);
        
        List<Participant> participants = Arrays.asList(participant1, participant2);
        
        TransactionResult result = coordinator.executeTransaction(transaction, participants);
        
        assertThat(result.isSuccessful()).isTrue();
        verify(participant1).commit(transaction);
        verify(participant2).commit(transaction);
    }

    @Test
    void testRollbackWhenOneParticipantVotesNo() throws Exception {
        when(participant1.prepare(transaction)).thenReturn(Vote.COMMIT);
        when(participant2.prepare(transaction)).thenReturn(Vote.ROLLBACK);
        
        List<Participant> participants = Arrays.asList(participant1, participant2);
        
        TransactionResult result = coordinator.executeTransaction(transaction, participants);
        
        assertThat(result.isSuccessful()).isFalse();
        verify(participant1).rollback(transaction);
        verify(participant2).rollback(transaction);
    }

    @Test
    void testTimeoutDuringPreparePhase() throws Exception {
        when(participant1.prepare(transaction)).thenReturn(Vote.COMMIT);
        when(participant2.prepare(transaction))
            .thenAnswer(invocation -> {
                Thread.sleep(2000); // Simulate timeout
                return Vote.COMMIT;
            });
        
        List<Participant> participants = Arrays.asList(participant1, participant2);
        coordinator.setTimeout(1000); // 1 second timeout
        
        TransactionResult result = coordinator.executeTransaction(transaction, participants);
        
        assertThat(result.isSuccessful()).isFalse();
        verify(participant1).rollback(transaction);
    }

    @Test
    void testConcurrentTransactions() throws Exception {
        when(participant1.prepare(any())).thenReturn(Vote.COMMIT);
        when(participant2.prepare(any())).thenReturn(Vote.COMMIT);
        
        List<Participant> participants = Arrays.asList(participant1, participant2);
        
        Transaction tx1 = new Transaction("TX1");
        Transaction tx2 = new Transaction("TX2");
        
        CompletableFuture<TransactionResult> future1 = 
            CompletableFuture.supplyAsync(() -> coordinator.executeTransaction(tx1, participants));
        CompletableFuture<TransactionResult> future2 = 
            CompletableFuture.supplyAsync(() -> coordinator.executeTransaction(tx2, participants));
        
        TransactionResult result1 = future1.get(5, TimeUnit.SECONDS);
        TransactionResult result2 = future2.get(5, TimeUnit.SECONDS);
        
        assertThat(result1.isSuccessful()).isTrue();
        assertThat(result2.isSuccessful()).isTrue();
    }

    @Test
    void testParticipantCrashDuringPreparePhase() throws Exception {
        when(participant1.prepare(transaction)).thenReturn(Vote.COMMIT);
        when(participant2.prepare(transaction)).thenThrow(new RuntimeException("Crash simulation"));
        
        List<Participant> participants = Arrays.asList(participant1, participant2);
        
        TransactionResult result = coordinator.executeTransaction(transaction, participants);
        
        assertThat(result.isSuccessful()).isFalse();
        verify(participant1).rollback(transaction);
    }

    @Test
    void testCoordinatorCrashRecovery() throws Exception {
        // Simulate coordinator crash after prepare phase
        when(participant1.prepare(transaction)).thenReturn(Vote.COMMIT);
        when(participant2.prepare(transaction)).thenReturn(Vote.COMMIT);
        
        List<Participant> participants = Arrays.asList(participant1, participant2);
        
        coordinator.simulateCrashAfterPrepare(true);
        TransactionResult result = coordinator.executeTransaction(transaction, participants);
        
        // After recovery
        coordinator = new Coordinator();
        coordinator.recover();
        
        verify(participant1, times(1)).rollback(transaction);
        verify(participant2, times(1)).rollback(transaction);
        assertThat(result.isSuccessful()).isFalse();
    }

    @Test
    void testIdempotency() throws Exception {
        when(participant1.prepare(transaction)).thenReturn(Vote.COMMIT);
        when(participant2.prepare(transaction)).thenReturn(Vote.COMMIT);
        
        List<Participant> participants = Arrays.asList(participant1, participant2);
        
        // Execute same transaction twice
        coordinator.executeTransaction(transaction, participants);
        coordinator.executeTransaction(transaction, participants);
        
        // Verify commit was only executed once per participant
        verify(participant1, times(1)).commit(transaction);
        verify(participant2, times(1)).commit(transaction);
    }

    @Test
    void testMaxParticipantsLimit() {
        List<Participant> participants = Arrays.asList(
            participant1, participant2, participant3,
            mock(Participant.class), mock(Participant.class),
            mock(Participant.class), mock(Participant.class),
            mock(Participant.class), mock(Participant.class),
            mock(Participant.class), mock(Participant.class)  // 11 participants
        );
        
        assertThatThrownBy(() -> coordinator.executeTransaction(transaction, participants))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("Maximum number of participants exceeded");
    }

    @Test
    void testTransactionLogging() throws Exception {
        when(participant1.prepare(transaction)).thenReturn(Vote.COMMIT);
        when(participant2.prepare(transaction)).thenReturn(Vote.COMMIT);
        
        List<Participant> participants = Arrays.asList(participant1, participant2);
        
        coordinator.executeTransaction(transaction, participants);
        
        List<TransactionLog> logs = coordinator.getTransactionLogs();
        assertThat(logs).isNotEmpty();
        assertThat(logs.get(logs.size() - 1).getTransactionId()).isEqualTo(transaction.getId());
    }
}