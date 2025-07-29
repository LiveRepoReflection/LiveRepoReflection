package distributed_tx;

public class ParticipantOperation implements TransactionOperation {
    private final Participant participant;
    private final Runnable operation;

    public ParticipantOperation(Participant participant, Runnable operation) {
        this.participant = participant;
        this.operation = operation;
    }

    @Override
    public boolean prepare() {
        return participant.prepare();
    }

    @Override
    public void commit() {
        participant.commit();
    }

    @Override
    public void rollback() {
        participant.rollback();
    }

    @Override
    public void execute() {
        operation.run();
    }
}