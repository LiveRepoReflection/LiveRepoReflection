import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.*;
import java.util.concurrent.*;

class DAOSimulatorTest {
    private Set<Integer> initialMembers;
    private DAO dao;
    private long testTimestamp;

    @BeforeEach
    void setUp() {
        initialMembers = new HashSet<>(Arrays.asList(1, 2, 3));
        dao = new DAO(initialMembers, 10000L, 60);
        testTimestamp = System.currentTimeMillis();
    }

    @Test
    void testInitialState() {
        assertEquals(10000L, dao.getTreasuryBalance());
        assertEquals(initialMembers, dao.getMembers());
    }

    @Test
    void testValidTransferProposal() {
        Map<Integer, Boolean> votes = new HashMap<>();
        votes.put(1, true);
        votes.put(2, true);
        votes.put(3, true);
        
        Proposal proposal = new Proposal(
            1, 
            1, 
            ActionType.TRANSFER_ASSETS, 
            "2,1000", 
            votes, 
            testTimestamp - 1000, 
            testTimestamp + 1000
        );

        assertTrue(dao.submitProposal(proposal, testTimestamp));
        assertEquals(9000L, dao.getTreasuryBalance());
    }

    @Test
    void testInvalidProposer() {
        Map<Integer, Boolean> votes = new HashMap<>();
        votes.put(1, true);
        
        Proposal proposal = new Proposal(
            1, 
            99, 
            ActionType.TRANSFER_ASSETS, 
            "2,1000", 
            votes, 
            testTimestamp - 1000, 
            testTimestamp + 1000
        );

        assertFalse(dao.submitProposal(proposal, testTimestamp));
    }

    @Test
    void testInvalidVotingPeriod() {
        Map<Integer, Boolean> votes = new HashMap<>();
        votes.put(1, true);
        
        Proposal proposal = new Proposal(
            1, 
            1, 
            ActionType.TRANSFER_ASSETS, 
            "2,1000", 
            votes, 
            testTimestamp + 1000, 
            testTimestamp + 2000
        );

        assertFalse(dao.submitProposal(proposal, testTimestamp));
    }

    @Test
    void testQuorumNotMet() {
        Map<Integer, Boolean> votes = new HashMap<>();
        votes.put(1, true);
        votes.put(2, false);
        
        Proposal proposal = new Proposal(
            1, 
            1, 
            ActionType.TRANSFER_ASSETS, 
            "2,1000", 
            votes, 
            testTimestamp - 1000, 
            testTimestamp + 1000
        );

        assertTrue(dao.submitProposal(proposal, testTimestamp));
        assertEquals(10000L, dao.getTreasuryBalance());
    }

    @Test
    void testConcurrentProposals() throws InterruptedException {
        int threadCount = 10;
        ExecutorService service = Executors.newFixedThreadPool(threadCount);
        CountDownLatch latch = new CountDownLatch(threadCount);

        for (int i = 0; i < threadCount; i++) {
            final int threadId = i;
            service.execute(() -> {
                Map<Integer, Boolean> votes = new HashMap<>();
                votes.put(1, true);
                votes.put(2, true);
                votes.put(3, true);
                
                Proposal proposal = new Proposal(
                    threadId, 
                    1, 
                    ActionType.TRANSFER_ASSETS, 
                    "2,100", 
                    votes, 
                    testTimestamp - 1000, 
                    testTimestamp + 1000
                );

                dao.submitProposal(proposal, testTimestamp);
                latch.countDown();
            });
        }

        latch.await(5, TimeUnit.SECONDS);
        assertEquals(10000L - (100 * threadCount), dao.getTreasuryBalance());
    }

    @Test
    void testAddMemberProposal() {
        Map<Integer, Boolean> votes = new HashMap<>();
        votes.put(1, true);
        votes.put(2, true);
        votes.put(3, true);
        
        Proposal proposal = new Proposal(
            1, 
            1, 
            ActionType.ADD_MEMBER, 
            "4", 
            votes, 
            testTimestamp - 1000, 
            testTimestamp + 1000
        );

        assertTrue(dao.submitProposal(proposal, testTimestamp));
        assertTrue(dao.getMembers().contains(4));
    }

    @Test
    void testModifyQuorumProposal() {
        Map<Integer, Boolean> votes = new HashMap<>();
        votes.put(1, true);
        votes.put(2, true);
        votes.put(3, true);
        
        Proposal proposal = new Proposal(
            1, 
            1, 
            ActionType.MODIFY_QUORUM, 
            "70", 
            votes, 
            testTimestamp - 1000, 
            testTimestamp + 1000
        );

        assertTrue(dao.submitProposal(proposal, testTimestamp));
        
        // Test that new quorum is enforced
        Map<Integer, Boolean> newVotes = new HashMap<>();
        newVotes.put(1, true);
        newVotes.put(2, true);
        
        Proposal newProposal = new Proposal(
            2, 
            1, 
            ActionType.TRANSFER_ASSETS, 
            "2,1000", 
            newVotes, 
            testTimestamp + 2000, 
            testTimestamp + 3000
        );

        assertTrue(dao.submitProposal(newProposal, testTimestamp + 2500));
        assertEquals(10000L, dao.getTreasuryBalance()); // Proposal should fail due to new quorum
    }
}